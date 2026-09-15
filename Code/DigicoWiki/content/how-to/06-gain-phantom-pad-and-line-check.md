# Set gain, phantom power and pad

## From the channel strip

The **input area** at the top of the strip shows analogue gain (big rotary), digital trim (small rotary), polarity, 48V and, on the Q225, the main/alt selector.

- Assign the channel (touch it so it goes gold). The big on-screen rotary follows the encoder above the strip; the button under that encoder flips **polarity**.
- Scroll the assign down one step and the encoder controls **digital trim** instead; its button toggles **gain tracking**.
- **48V** and the **pad** live in Channel Setup (touch the top of the strip). 48V shows as a red *48* on the socket in Audio I/O as well.

![Channel input area](/figures/gs-p014-1.png)

Gain, pad and phantom are properties of the **socket**, not the channel. Two channels patched to the same socket share them, and a monitor console sharing the rack sees them too (see [Conform the I/O racks](/how-to/09-conform-the-io-racks) for shared-rack control).

## From Audio I/O (whole rack at once)

Setup > **Audio I/O** > select the rack port on the left. Each socket in the graphic shows its number, name, gain at the bottom, and a red *48* when phantom is on. Touch a socket and the controls appear below the graphic. The **default rack** button resets every gain, pad, SRC and phantom setting on that port; don't press it during a show.

![Audio I/O socket display](/figures/ref-p150-1.png)

## Line check: listen to a socket before it's patched

In Audio I/O, turn on **Line Check**. Now touching any input socket, patched or not, shows its gain/48V controls and a **listen** button that sends that socket to the solo bus set for line check (Options > Solo > *Line check solo bus*). Gain is on the Touch-Turn encoder. This is the fastest way to check a stage box before the session is built.

![Line check controls](/figures/ref-p154-1.png)

## Gain tracking

With **GT** on, the digital trim moves opposite to any analogue gain change, so the channel level stays put. That's for when another console (or a shared rack in Receive Only) owns the preamp. On a single-console system leave it off.

Manual: [Reference 1.2.1 Channel Strip Input Area](/reference/1-2-channel-input-common-elements), [2.12.8 Socket Options](/reference/2-12-setup-menu).
