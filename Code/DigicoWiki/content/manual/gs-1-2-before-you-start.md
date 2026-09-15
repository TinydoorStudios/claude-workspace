# 1.2 Before You Start

*The Console — manual pages 7–15*

There are certain general operating principles and terms that should be understood before continuing to use this manual. Please read this chapter carefully before proceeding.

### 1.2.1 Worksurface Layout

**Channel processing**

![Q225 channel processing strip: Alt Input, HPF/LPF, 4-band dynamic parametric EQ, multiband dynamics thresholds; Master Section: headphones, USB port, master screen, macro control](/figures/gs-p007-1.png)

![Q225 master section and worksurface: master screen, macro control, solo, snapshot control, touch turn and talkback control, snapshot previous/next, assignable master fader, assignable rotaries and switches, mute/solo/TFT displays, channel faders](/figures/gs-p007-2.png)

**Rear Panel**

![Q225 rear panel: Ethernet ports, World Clock I/O, Optocore, MADI I/O, Display port, USB Audio, DMI Slots 1&2, Waves I/O port, Console USB, MIDI In/Out/Thru, GPIO, Dual PSU, 4 AES I/O, 8 mic/line in and 8 line out](/figures/gs-p008-1.png)

**IP Addresses on a QUANTUM 2**

The QUANTUM 2 Engine board contains 2 devices that require an IP address. The Console PC and the Host Interface controller. Both devices' IP addresses are displayed in the console diagnostics tab.

![Console diagnostics tab with the Console IP address and Host Interface IP fields highlighted](/figures/gs-p008-2.png)

Note: This IP address will be set to appropriate values when the console is shipped and they should not be changed in normal operation.

The IP Addresses for these devices can however be set using Network Settings in the Quantum Home interface. Quantum Home can be accessed using the Master screen > System > Quit To Windows function. This program allows the user to enter a single IP and subnet mask. This is the IP for the Console PC and the application will automatically set the Host Interface controller's IP to the correct sequential Address. Once the required IP or Subnet has been entered, a console power cycle is required for the change to take effect. Pressing the OK and Shut Down button will initiate the Shut Down Procedure.

### 1.2.2 Layers and Banks

The QUANTUM 2's worksurface is divided into Layers and Banks. Each Bank contains twelve channels, and the channels which are currently active on the control surface are defined using the fader bank and bank layer buttons to the right of the Channel Strip section's fader.

Note: There is also a Master Screen Assign button above the master fader on the centre section which is used to switch the right section to display the Master Screen.

![Fader bank and layer buttons: channel select, layer, screen assign, and bank buttons for Aux 1-12, CG 1-12, TB In, CG 13-24](/figures/gs-p009-1.png)

A 'bank' is a set of twelve faders, and a 'layer' contains up to four 'banks'. There are up to 3 'layers' in each section of the desk. Pressing the bank layer button, located above the fader bank buttons, toggles between layers. To access a bank of faders within that layer, press the appropriate fader bank button. To switch both sections of the console to the same bank level, press and hold one of the fader bank buttons. The specific channels which are contained within each Bank are defined in the Layout > Fader Banks display. By default, the Input channels will be assigned to Layer 1 of the console. The different output channels will be assigned to Layer 2. Control Groups will be assigned to Layer 2. These bank assignments can be customised by the user and saved in a session at any time.

### 1.2.3 Using the Control Surface

There are two main ways in which all of the functions of the QUANTUM 2 are accessed:

1. The touchscreen display, which can be controlled directly using a finger, or by using the keyboard and mouse
2. The physical encoders, switches and faders.

A number of functions can be accessed in different ways, allowing users to operate the console using whichever interface they prefer. This manual will describe accessing on-screen functions by touching the screen directly and not by using the mouse. All of the physical controls are described in full within the relevant section of the manual and many require no further introduction. The Master screen has a row of grey buttons across the top, which are used to access a range of configuration displays. Pressing these buttons opens either a further drop-down sub-menu or a pop-up display. If a drop-down menu is opened, pressing on one of its entries will open a pop-up display. The buttons lighten to indicate that their sub-menu or pop-up display is open. A number of the buttons within each pop-up display generate further pop-ups.

Generally, buttons within the pop-ups are coloured grey when their function is inactive, switching to a colour when their function is active. Pressing on a text box opens a numeric or QWERTY keypad which can be operated directly by pressing the screen or via the console's external keyboard. Pop-ups are closed by pressing the box in the top right-hand corner of the pop-up, marked CLOSE or CANCEL (or by pressing CAN on keypad pop-ups). On the Right-hand panel is a single encoder marked Touch-Turn (shown below). This is used to access any rotary controls within the Master Screen. To assign the Touch-Turn encoder to a particular on-screen pot, touch the pot to be assigned. You will notice that a coloured ring appears around the on-screen pot, indicating that it is assigned to the Touch-Turn encoder. The colour of this ring is unique to that control and is also reflected in the base of the Touch-Turn encoder, providing further indication of which pot is currently assigned to it.

![Touch-Turn encoder, talkback controls, snapshot previous/next buttons, and Master Screen button](/figures/gs-p010-1.png)

The Master Screen button on the right-hand section switches the right screen view from the Master Screen to the bank of channels which are selected in the right-hand section.

### 1.2.4 The Assigned Channel

One of the channels in the Channel Strip panel is displayed in gold, indicating that it is currently the Assigned Channel. This means that it has been assigned to the worksurface controls and can be configured in detail, as described below. To Assign a channel, touch anywhere in the channel on the screen (except the Aux Send area or the meters at the top of the screen). Alternatively, use the ch left and right buttons at the bottom of the channel worksurface controls to scroll through the channels in the panel:

![Channel select buttons, channel strip fader, and row of twelve assignable rotary encoders](/figures/gs-p011-1.png)

Note that these left and right arrows are duplicated in the channel Setup and Output displays. Note also that the Channel List display provides another method for assigning a channel to the worksurface controls.

Once a channel is assigned, all of the controls for that channel which are not displayed within the channel strip itself can be accessed via secondary pop-ups, displayed by touching inside the relevant area of the channel. These pop-ups include controls such as input and output routing and signal processing parameters. A number of the physical rotary encoders on the control surface can be assigned to different on-screen pots. In order to ensure that it is clear which function is assigned to which encoder, the assigned on-screen pot will have a coloured ring around it which will be reflected in the colour of the light around the base of the encoder on the control surface.

![Touch-Turn encoder and Master Screen button](/figures/gs-p011-2.png)

![Row of twelve assignable encoders below the touchscreen, with 2nd Function and Option/All buttons at each end](/figures/gs-p011-3.png)

The row of twelve encoders and buttons immediately below the touchscreen (shown above) refer to the channels with which they are aligned.

Pressing one of the Quick Select buttons on the left of the screen will assign the selected function to the row of these controls below the screen. Five aux sends can be displayed in the Channel Strip panel at any one time. If more than six aux sends have been created in the session, the scroll button outside the bottom left-hand corner of the screen can be used to scroll the display through the remaining auxiliaries.

![2nd Function and Option/All buttons with channel up/down; full channel-processing strip showing EQ and dynamics rotaries](/figures/gs-p012-1.png)

The controls to the right of the Channel Strip panel allow the Assigned channel to be adjusted:

The top half of the channel worksurface controls (down as far as the insert a, insert b and direct buttons, as shown above) control the signal processing parameters which are displayed in the pop-ups accessed by touching in the appropriate section of the active channel. The bottom half of the channel worksurface controls is concerned with output routing.

To the left of the screen are more channel controls: when pressed, the 2nd function button allows access to different parameters:

1. Stereo Aux Pan and Pre/Post switching
2. Hard Mute of a channel
3. Switching of LR or LCR panning

2nd function is indicated by a green 2nd Function display appearing in the bottom left-hand corner of the screen, as well as by the 2nd function button lighting with a ring of green.

The Option/All button has 2 main functions:

1. When pressed and released, any channel that is a member of a gang or Multi will be temporarily isolated from that gang or Multi.
2. When pressed and held, any parameter that is adjusted on a single channel will also be adjusted in the same way on all of the channels in that bank.

### 1.2.5 The Master Fader

By default, the fader in the bottom right corner of the right worksurface is assigned to the Master buss, which is the lowest numbered stereo group output by default. In addition, this fader can be reassigned to control any input channel or buss of your choice using the Layout>Fader Banks panel. Press the Assign master fader button and the Channel List will be displayed. Select a channel by touching its entry in the Channel List and it will be assigned to the Master Fader. The fader can also be unassigned (set to empty) by pressing the Unassign master fader button.

![Layout > Fader Banks screen with the Assign master fader button called out, and top of the Channel List display](/figures/gs-p013-1.png)

![Channel List display with a channel entry highlighted for selection](/figures/gs-p013-2.png)

### 1.2.6 Channel Types

The QUANTUM 2 has 4 different channel types which are laid out in banks of 12 on the console worksurface and can be identified by their colour. By default, the Input Channels will be assigned to Layer 1 on the left and right sections of the console. The output channels (Groups, Auxes and Matrices) will be assigned to Layer 2. Control Groups will be assigned to Layer 2. These bank assignments can be customised by the user and saved in a session at any time. Holding any left or right section bank or layer button down for a couple of seconds will switch the left and right worksurface sections to the same bank level or layer. The controls on each different type of output channel are identical but an input channel has a number of additional of features.

![Q225 channel type comparison: Inputs, Groups, Auxes, Matrix screens with Input Module, Analogue Gain/Digital Trim, HPF/LPF, Insert A, 4-band Dynamic EQ, Multiband Dynamics, Insert B, SD/Mustard switch, Aux Sends, Channel Pan, Mute Indicators, Channel Label, Routing Module, Gang & Safe Indicators](/figures/gs-p014-1.png)
