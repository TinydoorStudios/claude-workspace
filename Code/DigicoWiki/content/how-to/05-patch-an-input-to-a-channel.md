# Patch an input to a channel

The route from a stage-box socket to a fader is set in the channel's **Setup** panel.

![Channel Setup panel (touch the top of the strip)](/figures/q2-channel-setup.png)
*Channel Setup panel (touch the top of the strip) — Quantum 2 offline software, V22.*

![Input Route panel: ports, signal groups, signals](/figures/q2-input-route.png)
*Input Route panel: ports, signal groups, signals — Quantum 2 offline software, V22.*

1. Touch the **top** of the channel strip (the input/filters area) to open Channel Setup. Or Layout > Channel List > **Edit** on, expand *Input Channels*, touch the *main input* box for that channel.
2. Pick **mono** or **stereo** at the top before anything else; it changes what the panel offers.
3. Press the **main input** routing button (grey). The Input Route panel opens with three columns: **ports** on the left (Local I/O, each rack, DMI cards, internal sources), **signal groups** in the middle, **signals** on the right.
4. Touch the socket. Blue means selected. An input takes one signal (two for stereo), so a new selection replaces the old one.

![Channel Setup panel](/figures/ref-p029-1.png)

![Input Route panel: ports, signal groups, signals](/figures/ref-p030-1.png)

## Patch a whole run at once (ripple)

At the top of the Input Route panel, set the **ripple channels** count (grey numbered buttons or the keypad), then touch the first socket. Channels 2, 3, 4… take the next sockets in order. Ripple can follow channel number or fader-bank order; channel number is the default.

## Alt input

Every mono channel has a **main** and an **alt** input. The *main* button in the strip is grey on main, red on alt. Route the alt in the same panel with the *alt input* button. Alt inputs keep their own digital trim.

## Naming

By default the channel takes the socket's name. Touch the name box in Setup (or in Channel List with Edit on) to type your own. Once you've named it manually the name stops following the input; clear the name and re-select the input to get automatic naming back. See [Name channels and sockets](/how-to/10-name-channels-and-sockets).

Manual: [Reference 1.4.3 Input Routing](/reference/1-4-input-channel-specific-functions), [Getting Started 1.7 Routing Basics](/console/1-7-routing-basics).
