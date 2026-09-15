# 2.9 Control Groups

*Chapter 2: The Master Screen — manual pages 139–143*

### 2.9.1 The Master Control Groups Display

An overview of all the Control Groups within a session can be access via the Control Groups menu button in the master panel.

![Control Groups (manual p.139)](/figures/ref-p139-1.png)

This display contains basic channel strips for each Control Group. Each channel strip includes a list of channels that are assigned to that control group and few basic controls that can be adjusted from within the control group view, including spill, join/leave, clear and all mute. The Control Group naming controls are also available within the display’s channel strips.

Any number of input channels and output channels can be assigned to one or more of the Control Groups. Channels assigned can all be adjusted from a single worksurface control assigned to that control group. This means that changes to the Control Group fader, mute or solo will be applied to all of the channels assigned to that Control Group.

There are 2 methods to set up Control Groups:

1) Press the LCD Function button on the CG fader bank followed by the JOIN CG button, then press the channel select button for the CG that you want to use, then press the channel select buttons for each of the channels to be included in the CG, finally deselect the JOIN CG button:

Press LCD function button, then join CG

![Control Groups (manual p.139)](/figures/ref-p139-2.png)

Press LCD function button, then join CG

Select Control

Press channel LCD buttons to

Labels: Group to join · assign members · 2.9 Control Groups

2) Press the on-screen JOIN/LEAVE button for the required CG channel;

Press the channel select buttons for each of the channels that you want to make members of the CG; Release the JOIN/LEAVE button:

![Control Groups (manual p.140)](/figures/ref-p140-1.png)

List of members

![Control Groups (manual p.140)](/figures/ref-p139-2.png)

Press channel LCD buttons to assign members

Press join/leave button on required CG channel

A list of all the connected channels and their names is displayed above each Control Group display.

You can also clear all the channels from a Control Group by pressing Clear.

When a channel is a member of a Control Group, its own controls can still be adjusted independently of the other Group members. Adjustments to fader levels are transmitted to the Group members as dB changes, so that a level increase of 2dB on the Group fader will increase all the member levels by 2dB, irrespective of the relative levels of the individual channel faders.

Note: Control Group channels function completely differently from Group channels: Group channels mix together the audio from any channels routed to them, whereas Control Group channels simply move the channel faders of any channels assigned to them, irrespective of any audio routing.

The number of control groups available is defined in the console Session Structure. Control Groups can be named using the standard naming tools. The safe button, located at the bottom of the on-screen channel strip, can be used to protect the assignments and settings of the Control Group from being changed if a new Snapshot is fired.

All of the Control Groups to which an input or output channel belongs to are displayed immediately above the GANG and SAFE buttons in the Channel strip panel.

Note: Only the first two to three Control Group assignments within a channel can be displayed in the channel strip.

2.9 Control Groups

All of the channels included in a Control Group are listed in the top half of the Control Group channel strip display. To clear all of the channels currently assigned to a Control Group, touch the Control Group’s clear button, located below the join/ leave button, and press Yes in the warning display that appears.

### 2.9.2 Control Group Fader Modes

There are three modes in which the Control Group fader can interact with the faders of the channels assigned to it, and the button below the clear button in the channel strip display toggles between them:

In moving fader mode, all assigned faders will move to replicate any Control Group fader movements.

Note: It is the level change associated with the fader movement which is replicated, not the physical distance the fader is moved.

In VCA style mode, moving the Control Group fader affects the output level of all assigned channels without moving their faders. In mute only mode, the Control Group only controls the mute buttons of assigned channels, not the output level.

Note: In all three modes, moving the fader of a channel assigned to a group does not impact the output levels of other channels within the group.

### 2.9.3 Control Group Mute Functions

The mute buttons within a Control Group interact in the same way, regardless of the current fader mode:

The mute button above the LCD display on a Control Group fader can be used to mute all of its assigned channels. Its function is duplicated by the all mute button below the channel’s scribble strip. When a channel is muted by its Control Group mute button, the channel's mute button lights in the normal way. The channel's CG mute button goes blue to indicate that the Control Group mute button (rather than the channel mute button) is responsible for the mute. When deactivated, the Control Group mute button returns all assigned channels to their mute state before the Control Group mute button was activated.

CG Mutes are treated as “in series” where a channel is a member of more than one group. All CG mutes must be off for a channel to be unmuted; any CG muted always mutes all of its members.

If a channel is CG muted by single or multiple CGs, the worksurface channel mute button will override all CG mutes for that channel. The channel will not however be removed from CG membership so if the relevant CG is muted again, the channel will also be muted.

The auto-mute function, activated by touching the auto-mute button located above the Control Group name in the Channel Strip panel, automatically mutes any channel which is removed from that Control Group and unmutes any channel that joins the Control Group.

2.9 Control Groups

### 2.9.4 Control Group Spill (1272+)

Members of a control group can be spilled directly rather than adding them to a spill set. They can be spilled by using the Spill button on the CG channel strip and the Control Groups panel, or by firing a “Spill Control Group” macro under the Layout command type.

![Control Groups (manual p.142)](/figures/ref-p142-1.png)

Spill members of the CG

### 2.9.5 Control Group Aux Send Enable (v1445+)

The aux sends button in the Control Group channel strip allows individual CG faders to control Aux send levels when the Aux to fader function is active. The Control Group fader acts as a trim for all Aux sends on the selected (soloed) Aux buss.

An Aux Send Enable macro is included in Setup>Macros under the Control Group command type.

![Control Groups (manual p.142)](/figures/ref-p142-2.png)

![Control Groups (manual p.142)](/figures/ref-p142-3.png)

Include/exclude CG from CG controls Aux Sends.

Note that the CG Fader Controls Aux Send global setting in Options>Faders has been removed in V1445.

2.10 Solos Menu
