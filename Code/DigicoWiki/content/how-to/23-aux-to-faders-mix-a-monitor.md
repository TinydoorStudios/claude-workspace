# Mix a monitor send on the faders (Aux to Faders)

Solo an aux and the channel faders become the sends to that aux. That's the default behaviour (Options > Solo > *Solo assigns aux sends to faders*, on by default) and the fastest way to build a wedge or IEM mix.

1. Go to the outputs layer and press **solo** on the aux. The input faders jump to their send levels for that aux; the top row of encoders also takes the sends (*Solo assigns aux to top encoders*).
2. Move faders. What you hear on the solo bus is that aux, post its own processing if **True Solo** is on.
3. Press the aux's solo again (or Clear) to return the faders to channel levels.

Layout > **Aux to Faders** lists every aux; touching one activates aux-to-faders without soloing. **clear on close** drops the assignment when the panel closes. Macros exist for the same thing.

![Layout > Aux to Faders: one button per aux](/figures/q2-aux-to-faders.png)
*Layout > Aux Sends to Faders — Quantum 2 offline software, V22.*

## Send points

Each send can be pre-fade, pre-mute, mid EQ/dyn, pre-EQ/dyn, pre-processing or post-fade. Set it per channel with 2nd Function and the aux row buttons, or globally from the aux's own Setup panel. Monitor sends are normally pre-fade.

## Pans on stereo auxes

With 2nd Function held, the aux row encoders become pans. The aux's Setup panel can link (or reverse-link) every channel's aux pan to the channel pan. V22 also copies pan data when you use *copy levels* in aux setup.

## Aux Nodes panel

![Layout > Aux Nodes asks for an input or group channel to be selected first](/figures/q2-aux-nodes.png)
*Layout > Aux Nodes with no channel selected: pick an input or group channel first — Quantum 2 offline software, V22.*

Layout > **Aux Nodes** shows either every send from one channel or every contribution to one aux (**input/groups** vs **aux buss** view, with *follow selection* to tie them). From here you can **solo a node**, and on Quantum add **nodal processing** (an EQ and dynamics on one send only) with **Add**, **Bypass**, **Remove**. Nodes can be safed individually.

![Aux Nodes panel](/figures/ref-p037-1.png)
*Manual figure: Aux Nodes panel, input/groups view — aux sends per channel — SD Quantum Software Reference, Issue H, p.37.*

## Control groups as trims

With **aux sends** enabled on a CG (see [Control groups](/how-to/21-control-groups-vca)), the CG fader becomes a ±18 dB trim for its members' sends to the soloed aux. In V22 group faders can be included via Options > Solo > *Aux to Faders includes Group*.

## Copy a mix

The aux's Setup panel has **copy levels** to copy sends from another aux (and, with KLANG active, *copy to KLANG*).

Manual: [Reference 1.4.9 Aux Buses](/reference/1-4-input-channel-specific-functions), [1.4.10 Aux Nodes](/reference/1-4-input-channel-specific-functions), [2.3.5 Aux to Faders](/reference/2-3-layout-menu).
