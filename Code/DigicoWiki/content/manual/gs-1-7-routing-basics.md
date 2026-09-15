# 1.7 Routing Basics

*The Console — manual pages 23–25*

### 1.7.1 Selecting Inputs & Outputs

All channel input, output, insert send and insert return routing is done via routing displays, accessed via the dark grey routing buttons in the channel Setup and Output displays (shown below for an Input channel’s input).

Note that multi-channel signals are routed individually, and then collected together as a "Multi Channel" as described in the SD/Quantum Software Reference Manual To access Channel Input Setup, touch the top of an input channel display on the touchscreen. To access Channel Output Setup, touch the bottom of any channel type's display on the touchscreen. It is also possible to configure channel input and output routing directly from the Channel List display: Activate the Edit button at the bottom of the display, then touch the input route box for a channel. A standard Setup display will then appear, from which a Routing display can be opened. Inserts and Outputs can also be routed from this display by touching in the appropriate column.

![Routing Basics (manual p.23)](/figures/gs-p023-1.png)

Within each display, there are three columns containing three levels of routing selection: - The left-hand column contains the available ports within which the desired input or output might be located; - The middle column, signal groups, then shows the available groups of inputs or outputs within that port; - The right-hand column, signals, then displays the individual inputs or outputs available within that signal group. The boxes in each column are lit blue to indicate that they are currently selected. If there is already a routing assigned within the display, the port and signal group columns containing the current assignment will be half-lit. Each output can only have one channel routed to it. The outputs that are currently in use by another channel display in blue text. If you attempt to route a different channel to an output which is already in use, a confirmation box appears, indicating which channel is already using it, and warning that continuing with the action will cause the old channel to be unrouted from this output. Press Yes to proceed, No to cancel.

Note that when routing direct outs from Input channels or outputs from output channels, any number of available signals can be selected. A new route selection will therefore be added to previous selections in these cases. However, inputs, insert sends and insert returns can only route to/from one signal (in the case of mono channels) or two signals (in the case of stereo channels). A new route selection will therefore result in the previous selection being lost for inputs and insert sends and returns. For stereo channels, left and right routes are presumed to be consecutive: When routing stereo signals, select the left route, and the next signal in the list will be automatically selected as the right route. If the last signal in a signal group or port is selected as the left route, the first signal in the following signal group or port will selected as the right route.

1.7 Routing Basics

Note: The outputs for the channel being routed are locked out of the signal list

Note also that the console views all routes as a single list. Therefore, if the left signal is connected to the last signal in a port, the right signal, will be automatically connected to the first signal of the next port, regardless of port type.

### 1.7.2 Ripple Channels

The ripple channels function, located at the top of the route display, allows consecutive channel routes to follow the routing of the current display incrementally. For example, Channels 1 to 8 direct outputs can be routed to Rack 1 > Line outs 1 to 8 respectively by routing Channel 1’s direct out to Rack 1 > Line out 1 and allowing the ripple channels function to route Channels 2-8 automatically. The number of channels to be rippled is defined either by selecting the appropriate grey numbered button, or by selecting the keyboard button to the right of the numbered buttons, typing the required number of channels (8 in the example above) into the numeric keypad which appears, and pressing OK. Once you have configured the ripple channels function, any routing action will also effect the appropriate number of channels above the channel being routed. The ripple channels function treats stereo channels as two channels. In other words, if Channel 2 in the above example is stereo, the ripple channels function will route Channel 1 to Line out 1, Channel 2 Left and Right to Line outs 2 and 3, Channel 3 to Line out 4 etc. The Ripple by bank/ channel number function changes how the channels are rippled, Ripple by bank ripples the channels by their position in the bank irrespective of channel number, Ripple by Channel number routes the rippled channels by channel number irrespective of position within the bank.

1.8 Channel Processing

### 1.7.3 Channel Names

The black and white text box in the Setup display is used for naming the channel. Channel names are displayed in the scribble strip at the bottom of the screen. By default, the channel is given the same name as the selected input signal. Note that if no input signal is selected, the scribble strip simply displays the channel number, prefixed by ch for Input channels, and prefixed by Aux, Grp or Matrix in the case of output channels. The following notes are specific to naming channels: The Next button moves the entire Setup display to the next channel. At the very top of the channel, the channel number and input signal name are displayed for Input channels, and the channel type and number are displayed for output channels. These labels remain unchanged, regardless of any channel naming.

For Input channels, note that if the channel input signal is changed once a channel has been manually named, the channel name will no longer follow the input signal name. To reactivate the automatic channel naming function, clear the name and re-select the channel input. Note also that the channel Output display also provides access to this channel naming facility. Channels can also be named directly in the Channel List display (in the Layout menu). Open the display, activate the Edit function below the list, and expand the required channel type list by touching its row. Touching the channel name column for any channel in the list will cause a keyboard pop-up to appear, where a name can be typed in the usual way.
