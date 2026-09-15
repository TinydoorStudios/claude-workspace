# 1.3 Channel Output and Inserts - Common Elements

*Chapter 1: Channel Types & Function — manual pages 23–28*

### 1.3.1 Channel Strip Output Area

The Channel Strip Output Area (Figure 13) makes up the lower half of the Channel Strip (Figure 1). This is where the channel output routes are configured (including Aux sends in the case of Input channels). Some basic output and insert functions are found in the channel strip. However, most of the output and insert parameters are contained in the channel Output display, accessed by touching the channel’s output or insert areas.

![Channel Output Display](/figures/ref-p023-1.png)
*Channel Output Display*

On Input channels, the lower part of the channel strip contains the aux sends (Figure 14). For all output channel types, there is a channel meter displayed in place of aux outputs (Figure 15). On stereo and multi channels, symbols below each meter indicate which signal they correspond to. LFE meters are indicated by a small box with a dot in it.

Note: input channels can display a meter in the top section of the channel strip.

Meter sources are defined in the Options menu, described in Chapter 2: Master Section. Below the meters section of output channels, there is an FX Output button (Figure 15). This button brings up either the controller display for the effects preset that has been assigned, or the FX Presets display if no preset has been assigned.

Note: that below the aux section of an Input channel, there is a pan control in place of the FX Output button. When an effects preset has been assigned to that channel's Direct Out, touching this pan control brings up the FX preset controller display.

1.3 Channel Output and Inserts - Common Elements

Below the channel name (Figure 16), there is indication of the lowest group (Grp:) output (along with indication of the lowest direct output (Dir:) in the case of Input channels), and indication of any control group (CG:) to which the channel belongs. The on-screen channel has MUTE and HARD (mute) indicators located above the Channel Name.

**Hard Mute**

Pressing the worksurface Mute Button of a channel silences all outputs from the channel apart from any which have been assigned pre-mute (this option is available for auxes and direct outs). Pressing the worksurface 2nd Function button to activate the Hard Mute silences all outputs from the channel, including those which are assigned pre-mute. A dedicated Hard Mute button for the selected channel can also be found on the worksurface of relevant consoles.

Immediately below the HARD button, there is a numeric display of the channel’s main fader value in dB. Below the MUTE button there is a CG MUTE Indicator which shows when the channel is muted as the result of its membership of a muted Control Group. In the bottom left-hand corner of the channel strip, there is a GANG display. To the right of the GANG button there is a SAFE button. This indicates that one or more of the channel's recall safes have been activated

Note: Multi channels do not have their own insert controls – each multi-channel component's insert points are configured individually.

Note: An Input channel’s aux display is opened by touching the aux area. To open the Output display, touch in the muting and naming area below the pan control.

1.3 Channel Output and Inserts - Common Elements

### 1.3.2 Channel Strip Insert Area

Each channel also has two inserts: insert A and insert B.  Both inserts follow the format (mono or stereo) of their channel. The channel strip insert areas are located above the EQ Section (Insert A) (Figure 17) and below the 2nd Dynamics Section (Insert B) (Figure 18), and their signals are sent and returned to that position within the signal path: insert A is pre-signal processing (but post filters), and insert B is post signal- processing (SD- see below for Quantum). Only one point, either insert A or insert B, can be used per channel on SD9 or SD11.

Channel strip insert areas include a button for switching that insert send on and off. The button is grey when the send is off, and red when it is on. Below the on/off button, there is a display of the current insert routing. The send route is displayed on the left, with the prefix “S:”, and the return route is displayed on the right, prefixed by R: (Figure 19). If no routing has been selected, these areas are blank apart from these prefixes. If the channel is stereo, only the left side of the insert routing is displayed.

**Post Fader Inserts**

Up to 32 mono input channels (SD) can have their insert B point switched to a post fader insert point using the button in the Channel Output display (Figure 20).

![Channel Output Display](/figures/ref-p025-1.png)
*Channel Output Display*

**Inserts on Quantum Consoles**

On Quantum consoles, there are 5 selectable insert positions available on every channel. These are: pre-fade, mid EQ/dyn, pre-EQ/dyn, pre-processing and post-fade. These are shared between Inserts A & B, and Mustard processing. One of these items can be placed in each insert position, and each one can go in any of the 5 selectable positions (provided neither of the other items are using that particular insert point).

1.3 Channel Output and Inserts - Common Elements

### 1.3.3 Console Output and Insert Routing

The Output displays for all channel types allow direct routing either to the external IO racks, or to one of a variety of internal locations, for both the channel’s main output (or direct output in the case of Input channels), and its insert send and return. In addition to touching inside the output area of the channel strip, it is also possible to open each channel's output display from the Channel List Display (Figure 21), opened from the Master Screen menu Layout > Channel List. Activate the Edit button at the base of the display, expand the required channel type by touching its entry in the list, then touch the output column within the required channel row. An outputs display will open within the Master Screen.

![Channel List Display](/figures/ref-p026-1.png)
*Channel List Display*

Towards the bottom of the Outputs display, there are three buttons marked output (direct in Input channels), insert A and insert B. Selecting one of these buttons opens the Signal Routing Area. When either insert is assigned, the ins A send or ins B send routing button appears in the left-hand column, and the ins A return or ins B return routing button in the right-hand column; When the output (direct output in Input channels) is assigned, the outputs (direct outs in Input channels) routing button appears in the left-hand column and the right-hand column is left blank. Pressing any of these routing buttons opens a routing display (Figure 22).

An extra button labelled send+return is included above the ports list in the Insert Send Route display button (Figure 23). When this button is activated, the send and return routing is linked for all signals within the INTERNAL port; if Graphic EQ 1’s input is assigned to the insert send, then Graphic EQ 1’s output is automatically assigned to that insert return. Similarly, if it is the return which is manually assigned, the send automatically copies that send assignment. The send+return button is grey when inactive and brown when active (Figure 24).

1.3 Channel Output and Inserts - Common Elements

![Direct Out Display](/figures/ref-p027-1.png)
*Direct Out Display*

![Insert Send Route](/figures/ref-p027-2.png)
*Insert Send Route*

![Insert Return Route](/figures/ref-p027-3.png)
*Insert Return Route*

The mono > mono and mono > stereo buttons are used when routing a mono channel to internal FX units and Waves plug-ins (where available). When mono > mono is selected, the channel signal is routed to left side of an FX unit, or to a mono Waves rack input. When mono > stereo is selected, the channel is routed to both sides of the FX unit or Waves rack.

### 1.3.4 FX Presets

Each channel output or insert send can be sent to an internal FX Unit. Pressing the fx presets button at the bottom of the Outputs display brings up the fx Presets display. Or pressing the FX Output button available on Aux, Group and Matrix channels.

The fx preset is applied to whichever channel output is active in the Outputs display when the fx presets button is pressed: the main channel output (or direct output), insert send A or insert send B:

![Channel Output and Inserts - Common Elements (manual p.27)](/figures/ref-p027-4.png)

For more details of SD and Quantum FX and FX preset management, please refer to Chapter 2: The Master Screen.

1.4 Input Channel – Specific Functions
