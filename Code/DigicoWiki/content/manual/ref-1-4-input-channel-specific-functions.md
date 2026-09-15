# 1.4 Input Channel – Specific Functions

*Chapter 1: Channel Types & Function — manual pages 28–43*

### 1.4.1 Gain Tracking

The gain tracking option allows the trim level to compensate automatically for any adjustments made to the analogue input level. If the analogue input level is increased, the trim level will decrease to keep the channel signal level the same (Figure 25). This function is particularly useful when the analogue level is being controlled from another console, such as when one console is running monitor mixes and another console is running Front of House. Control of the trim rotary and track on/off button can be assigned to the encoder and button above/below the channel using the assign scrollers to the left of the encoders, or the quick select buttons.

### 1.4.2 Relative Gain-Tracking - Snapshot Recalls Total Gain

Relative Gain-Tracking is implemented as a Snapshot Recalls Total Gain option at the bottom of the Snapshot Global Scope panel (Figure 26). When a snapshot recalls an input channel trim, it compares the snapshot's stored analogue gain against the current gain on the channel's input socket. If there's a difference, it offsets the value recalled by the trim. This only happens when the socket's rack is in Receive Only, or the analogue gain is not in Recall Scope.

![Snapshot Global Scope panel (Figure 26)](/figures/ref-p028-1.png)

Note: more information on snapshots and scope is available in Chapter 2: The Master Section.

### 1.4.3 Input Routing

Inputs are routed using the Channel Setup display, opened by touching the input area of the channel strip (Figure 25). It is also possible to open this display from the Channel List display, accessed via the Master Screen menu Layout > Channel List. Activate the Edit button at the base of the display, expand the required channel type by touching its entry in the list, then touch the main input column within the required channel row. A Setup display will open within the Master Screen (Figure 27).

![Channel List with Setup display (Figure 27)](/figures/ref-p029-1.png)

The buttons at the top of the channel Setup display define the format of the channel: mono or stereo.

Note: Multi-channel formats are configured in a different way from mono and stereo formats, as described later in this chapter.

The channel format affects a number of functions within the Setup display, therefore it is advisable to select the format before any further configuration takes place. The current format of the channel is indicated in the channel strip by the number of meters displayed: one meter for mono channels and two for stereo.

For mono channels, each input channel has two inputs: a main input and an alt(ernative) input. These are selected using the 'main' button in the channel strip. The button is grey when the main input is selected and red when the alt input is selected. The input can also be selected using the main and alt buttons towards the top of the Setup display. These buttons light to indicate which one is currently selected (Figure 28). For stereo channels, the alternative input becomes the right side of the stereo input, and therefore no main and alt input selection buttons are shown.

![Alt input in Channel Setup (Figure 28)](/figures/ref-p030-1.png)

Note: the inputs available on an Input channel include feeds from the external IO racks, the local inputs on the back of the console and a variety of internal signals. Pressing either the main input or alt input routing button in the Setup display opens the Input Route display.

(V1260+) Input Channels can be ripple routed by pressing or typing in the number of channels to be routed, then pressing the first input route source. There are two options for ripple routing: channel number or fader bank. Channel number is the default selection and routes channels in channel number order — so, if the first three channels in the bank are Ch 2, Ch 1, Ch 3, ripple routing from local IO gives Mic 2, Mic 1, Mic 3. Fader bank routes the channels in the order that they appear on the bank, so the routing in the example gives Mic 1, Mic 2, Mic 3.

![Ripple routing controls in the Main Input Route display](/figures/ref-p030-2.png)

### 1.4.4 Input Configuration

If a channel is stereo, balance and width controls appear below the mono and stereo buttons. The left-hand blue on-screen rotary controls the balance and can be reset to centre by pressing the centre button below it. The right-hand blue rotary affects the width of the stereo signal, with a range from mono to wide. The width can be reset to stereo by pressing the stereo button beneath the width rotary. The value of the balance and width is displayed to the right of each rotary as a percentage divergence.

![Balance and width controls in a stereo channel's Setup display](/figures/ref-p031-1.png)

Stereo channels also have an m-s button, located above the input routing button, which switches in a decode function for replaying M-S signals as a normal stereo pair. There are three further buttons in this panel: L<>R swaps the channel's left and right outputs, L>L+R sends the left signal to both left and right busses, and R>L+R sends the right signal to both left and right busses.

### 1.4.5 Channel Metering

Channel meters can be displayed in the top section of the Input channel strip, in place of the input and filters areas (Figure 29). To do this, press the Assign up arrow (SD7, Q7), the Rotary Assign up arrow (SD8, SD10), or the Gain quick select and screen scroll up arrow (SD5, SD9, SD11, SD12, Q3, Q5), all located on the console's worksurface.

On Quantum consoles, switching the channel view from SD to Mustard will also switch the large meters at the top of the screen to display the relevant SD or Mustard dynamics metering. A small SD or M indicator shows which of the two options is active.

### 1.4.6 CG/HARD mute indicators on the Meterbridge (Q7/SD7/Q5/SD5)

*Not on the Q225.*

In the multi-layer meter view on consoles with meterbridges, there are indicators displayed for all three types of mute function: Channel mute, CG Mute and Hard mute.

![Meterbridge multi-layer meter view (Q7/SD7/Q5/SD5)](/figures/ref-p032-1.png)

### 1.4.7 Output Routing

Signals can be fed from Input channels to four different places: aux busses, group busses, insert sends and direct outputs. The top half of the output section of the Input channel strip contains the aux buss controls, as previously described. Touching under the pan controls opens the Output Display (Figure 30), from here the channel strip can be assigned to groups and to direct outputs. Outputs can be routed from the Channel List just like inputs (Figure 27).

![Output routes (Figure 30)](/figures/ref-p032-2.png)

### 1.4.8 Pan Controls

The controls are formatted to match the format of the buss with the most components:

- Where there are only stereo or LCR busses, a simple pan slider is shown (see below left). Move the slider to adjust the pan. A text box indicates the panning position as a percentage from the centre towards the right.
- Where there are LCRS busses, a two-dimensional panning scope is shown (see below centre). Move the central grey square to adjust the position. Text boxes indicate the left-right and front-back position.
- Where there are 5.1 busses, a two-dimensional panning scope is shown, along with a pink LFE level control (see below right). Move the central grey square to adjust the position. Text boxes indicate the left-right and front-back position, as well as the LFE gain.

To send a channel to the LFE channel of the 5.1 buss, the LFE level must be assigned to a rotary row. Pressing the rotary button then toggles the channel between being sent to the 5 channels but not LFE, just LFE, and both LFE and the 5 other channels of the buss.

There is also an LCR blend knob. This control allows adjustment of the amount of signal that is sent to the centre leg (where one exists) of a surround or LCR buss. In the extreme left or right position, no signal will go to the centre leg.

Note: the pan of the Assigned channel can be controlled using the worksurface joystick (SD5,7,8,10). The pan control can also be assigned to one of the encoder rows. LR/LCR Blend is adjusted using the 2nd function button.

*Not on the Q225.*

### 1.4.9 Aux Buses & Assignable Controls

Within an Input channel strip, each aux send has a level rotary and on/off switch to the right. The switch is grey to indicate that the send is off, and red to indicate that it is on. The send level is displayed in dB on the right of the channel strip, underneath the aux number.

The source display immediately to the right of the level trim (Figure 31) shows the point in the channel from which the aux send is fed:

| Console | Aux send source positions |
|---|---|
| SD | pre-fader, post-fader, pre-mute |
| Quantum | pre-fade, pre-mute, mid EQ/dyn, pre-EQ/dyn, pre-processing, post-fade |

![Aux send position (Figure 31)](/figures/ref-p034-1.png)

The source position can be changed by pressing the worksurface 2nd function button and using the buttons below the rotary encoders (with the aux assigned to that particular row of rotaries). The source for each aux can also be adjusted globally via the aux channel's Setup display.

On stereo aux sends, there is a pan control to the right of the on/off switch. This can be adjusted by pressing the worksurface 2nd function button and using the rows of encoders below the worksurface screen. The pan controls for each aux can be globally linked (or reverse linked) to the channel pan via the aux channel's Setup display.

At the bottom of the assigned channel SD7/Q7 worksurface controls, there are four dedicated aux encoders with buttons, which control four contiguous aux send rotaries and on/off switches for the Assigned channel. The auxes controlled by these encoders and buttons can be selected using the scroll buttons to the left of the top encoder, and are indicated by a purple ring on the on-screen aux sends.

![SD7/Q7 dedicated aux encoders, with the purple ring indicating the assigned sends](/figures/ref-p034-2.png)

*Not on the Q225.*

Note: this assignment is channel specific and will be recalled if the Assigned channel is changed and returned to that channel.

The encoders and buttons immediately below the Channel Strip can be used to control either the aux sends, or a separate function. This function is referred to as the 'locked' function, as it does not change when the auxes are moved. The button at the end of each row, next to the LCD display, flips the assignment of that row between the aux sends and the locked function.

Touching any on-screen aux send assigns the highest available encoder row to that send and assigns any other available encoder rows to the aux sends below it. The scroll button outside the bottom left-hand corner of the screen can also be used to change which auxes are assigned to the encoders (SD5,7,8,10).

Note: a maximum of six auxes can be displayed in the Channel Strip panel at once. The panel will always display the auxes assigned to the encoder rows below it. This means that the auxes controlled by the dedicated aux encoders in the channel worksurface controls may not be visible.

By default, the encoders control the aux level and the button controls the aux on/off status. However, by pressing the 2nd function button (located on the surface), the button becomes the aux's send position selector and the encoder becomes the pan control of a stereo channel. On mono auxes, the encoder has no second function.

It is also possible to show all of the aux sends for a channel in a single display and assign them to the rotaries beneath the screen. This is done by assigning the required channel to the aux controls (the assigned auxes will be displayed in dark purple with a dark purple surround) then touching one of the assigned auxes. The layout of the display indicates which encoder each aux is assigned to; if there are more sends than rotaries, the assignments become scrollable using the Screen Scroll function.

![Aux sends for a channel assigned to the under-screen rotaries (SD7 example, 36 sends)](/figures/ref-p035-1.png)

Once you have adjusted the auxes in this display, you need to close it manually before opening any other channel detail display.

(V1260+) Aux sends/nodes can be safed individually, which includes aux send level, aux on/off, node solo (Quantum only), nodal processing (Quantum only) and KLANG parameters. All aux nodes in a channel can still be safed together by pressing the all safe button in the expanded aux send panel or aux node panel. To safe nodes individually, press the node safe button, then press on the nodes to be safed, which will be indicated by the aux node text turning red. Once the safes are complete, press the node safe button again.

(V1455+) A more/less button has been added to the Aux Expanded panel that will increase the panel size to show up to 5 rows of aux sends depending on the session. These can be scrolled to assign them to under-screen rotaries.

![Aux Expanded panel — More/Less button and node safe controls](/figures/ref-p036-1.png)

Note: when folded, the amount of auxes displayed in the Aux Expanded panel will depend on how many rows of assignable rotaries a console has.

Note: further worksurface assignments of auxes is available via the Surface, Faders and Solo tabs of the Options menu.

### 1.4.10 Aux Nodes Panel (all consoles) and Nodal Processing (Quantum only)

In Layout > Aux Nodes, there is an input/groups button, and an aux buss button. The input/groups button will show the aux sends per channel for the last selected channel. The aux buss view will show all the channel contributions or group contributions to an aux buss. When in aux buss view, either channels or groups can be shown in the aux contribution panel — this is selected in the show section located at the bottom right corner of the panel.

![Aux Nodes panel — input/groups view](/figures/ref-p037-1.png)

![Aux Nodes panel — aux buss view, with the 129-256 channel-range button](/figures/ref-p037-2.png)

When a console has more than 128 input channels, the 129-256 button will become available.

Along the top and bottom of the panel are function buttons.

**Solo node** — each aux node can be soloed. This feature can also be accessed from the channel screen expanded aux panel or from the nodal processor control panel. The circular node on/off indicator will show a green "s" when nodal solo is active.

If Options > Solo > Solo Displays All Aux Sends is enabled, soloing either an input channel or an aux master will open the aux nodes panel with the appropriate view selected.

The follow selection button links the input/groups view and aux buss views together. If a node has been selected, switching between input/groups and aux buss view will show the sends for the selected channel. For example, in input/groups view, select aux 17; when the aux buss view is selected, this will show all the contributions for aux 17. If in aux buss view the node for Ch3 is selected, when the input/groups view is selected, the aux sends for Ch3 will be shown.

The bring to surface button will bring the selected channel or buss to the worksurface and open the nodal processing panel if active.

There are three Nodal processing mode buttons in the Aux Nodes panel:

- **Add** — touching add, then selecting an aux node, activates nodal processing for that aux send.
- **Bypass** — toggling this control temporarily bypasses the nodal processing on the selected aux send. This function is not recallable with snapshots.
- **Remove** — removes nodal processing from the selected aux send.

**Nodal Processing**

Each Aux node send can have SD Nodal EQ and Dynamics inserted in its audio path. The maximum number of aux nodes available simultaneously depends on the model of Quantum console. The number of nodes in use is displayed in the Diagnostics panel. Each nodal processor also has its own entry in snapshot scopes, and they are also included in the channel list.

If processing is active on a node, a purple P is displayed next to the node on/off button. This status will also be visible in the channel strip aux display. When the node is touched in the Aux Nodes panel, the processing controls will be displayed and assigned on the screen where that channel is located. Both the EQ and dynamics controls will be displayed at the same time. There is also a control panel for aux node functions located in the bottom right-hand corner.

![Nodal processing controls displayed on the channel screen](/figures/ref-p038-1.png)

**Nodal Processing Copying**

'Copy To', 'Copy From', and 'Copy From Channel' are available for Nodal Processing via a popup panel on the nodal processing expanded view. Processing can be copied from other nodal dynamics or SD channel strip dynamics — from the main channel strip or from other nodes.

![Nodal processing copy popup panel](/figures/ref-p039-1.png)

### 1.4.11 KLANG Nodes

KLANG Nodes can be activated on an aux send to allow control of the channel's KLANG parameters. A KLANG button is displayed in the expanded aux panel and the Aux Nodes panel after KLANG is enabled in the External Control panel (see Chapter 2 - 2.12.14).

To add or remove a KLANG node, press the KLANG button, which will turn purple to indicate edit mode, and press on the individual aux sends to activate or deactivate a KLANG node. A KLANG 'G' will appear in the aux send box to indicate a KLANG node. When the addition/removal of KLANG nodes is complete, press the KLANG button again to disable editing.

![KLANG Nodes — aux sends panel with the KLANG control panel](/figures/ref-p039-2.png)

When an aux send with a KLANG node is pressed, an expanded KLANG control panel is shown at the bottom right of the display. A KLANG 'orbit' is displayed in the left-hand side of the panel, which displays the KLANG source position. When pressed, this will show an expanded orbit in which positional data can be adjusted.

To the right of this are the individual KLANG parameter adjustments: azimuth, type, elevation and solo (indicated by a green KLANG 'G'). On the right-hand side are controls for the KLANG send level and an on/off toggle. All of these on-screen controls are assigned to the under-screen rotaries. In the top row of the panel there are 'copy' and 'copy from' buttons to copy the KLANG and aux parameters to another KLANG node.

When KLANG is active, a new copy to KLANG button is visible in the copy levels drop-down menu in the Aux master setup panel. This will copy the aux send levels to the KLANG levels for that mix and in that snapshot.

![Copy to KLANG button in the Aux Setup copy levels menu](/figures/ref-p040-1.png)

### 1.4.12 True Solo (Quantum only)

This function allows the user to copy any internal processing used on an output buss to the solo buss, so that they get a true representation of what the artist is hearing. Any changes to the buss processing are updated in real time to the solo buss. The True Solo controls are accessed from the Solos panel, or by creating a macro that will directly open the True Solo panel.

![True Solo panel (Quantum only)](/figures/ref-p040-2.png)

### 1.4.13 Insert Point Locations (Quantum only)

As with aux nodes, each insert point can be moved Post Fader, Pre-Fader, Mid EQ/Dyn, Pre EQ/Dyn and Pre Processing. Only one insert point can be in each location at any one time.

![Selectable insert point locations across channel strips (Quantum only)](/figures/ref-p041-1.png)

### 1.4.14 Group Outputs

Group outputs are routed from within the groups section of the channel Outputs display. Touching the mono button to the left of the display produces a list of available mono groups in the right of the display, and touching the stereo or surround format buttons produces a list of the other types of groups. These buttons light to indicate that it is their group outputs list which is currently displayed, and half-light to indicate that there is routing to busses of that format which isn't shown in the display. Touching any of the groups within each list routes the channel to that group. Each channel can be routed to as many mono and stereo groups as have been created.

![Group routing in the channel Outputs display](/figures/ref-p041-2.png)

Any mono groups being fed by a stereo channel will receive an L+R summed signal of the channel output. The lowest selected group output is displayed in the channel strip, below the left side of the channel name, and the currently selected direct output is displayed below the right side of the channel name. When a new session is created, the lowest numbered stereo group is always designated the Master (SD7/Q7), or the first of the largest group type (e.g. 5.1 group) is master (all other consoles). All input channels are routed to the master group by default, and the master fader(s) are assigned to it.

### 1.4.15 Mix Minus function on Quantum Consoles

A different Mono Mix Minus feed can be created at the Direct Output of any mono input channel.

1. Send all required signals (including the channel that is to be removed) to an existing Mono Buss, and note the name of this buss.
2. Open the Output routing setup on the channel that is to be removed, and in the Mix Minus section press the button for the Mix Minus buss you just created.

When this channel's Direct Output signal is now routed to a physical console or rack output, the channel's input signal will be removed from the direct output signal.

![Mix Minus routing setup on a channel's Direct Output](/figures/ref-p042-1.png)

### 1.4.16 Direct Outputs

Basic routing is described in your console's Getting Started section. Once the direct output has been routed, it is switched on by pressing the grey on button next to the output level meter in the grey area below the direct outs routing button. The direct out is taken post-fader by default but can be switched to pre-fader or pre-mute by pressing the button to the right of the on button. The current selection is displayed to the right of the button.
