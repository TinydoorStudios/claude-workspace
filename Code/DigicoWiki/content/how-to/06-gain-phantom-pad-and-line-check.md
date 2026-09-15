# Set gain, phantom power and pad

## From the channel strip

![Input channel strips: gain/trim and 48V live in the input area at the top](/figures/q2-channel-strip.png)
*Input channel strips: gain/trim and 48V live in the input area at the top — Quantum 2 offline software, V22.*

The **input area** at the top of the strip shows analogue gain (big rotary), digital trim (small rotary), polarity, 48V and, on the Q225, the main/alt selector.

- Assign the channel (touch it so it goes gold). The big on-screen rotary follows the encoder above the strip; the button under that encoder flips **polarity**.
- Scroll the assign down one step and the encoder controls **digital trim** instead; its button toggles **gain tracking**.
- **48V** lives in Channel Setup (touch the top of the strip); it also shows as a red *48* on the socket in Audio I/O. **Pad** is a rack-output property, not a Channel Setup control — see below.

![Channel strip anatomy: input module gain/trim, phase, main/alt select](/figures/gs-p014-1.png)
*Manual figure: Channel Strip Anatomy, Input Module — Getting Started 1.2.6 Channel Types.*

Gain, pad and phantom are properties of the **socket**, not the channel. Two channels patched to the same socket share them, and a monitor console sharing the rack sees them too (see [Conform the I/O racks](/how-to/09-conform-the-io-racks) for shared-rack control).

## From Audio I/O (whole rack at once)

Setup > **Audio I/O** > select the rack port on the left. Each socket in the graphic shows its number, name, gain at the bottom, and a red *48* when phantom is on. Analogue rack outputs show a yellow *-10* in that same spot when their pad is switched in — white when no pad. Touch a socket and the controls appear below the graphic. The **default rack** button resets every gain, pad, SRC and phantom setting on that port; don't press it during a show.

![Setup > Audio I/O with a rack port selected](/figures/q2-audio-io.png)
*Setup > Audio I/O with a rack port selected — Quantum 2 offline software, V22.*

![Audio I/O socket display](/figures/ref-p150-1.png)
*Manual figure: The Socket Display — Reference 2.12.5.*

## Line check: listen to a socket before it's patched

In Audio I/O, turn on **Line Check**. Now touching any input socket, patched or not, shows its gain/48V controls and a **listen** button that sends that socket to the solo bus set for line check (Options > Solo > *Line Check Listen*). Gain is on the Touch-Turn encoder. This is the fastest way to check a stage box before the session is built.

![Line check controls](/figures/ref-p154-1.png)
*Manual figure: Socket Options — Line Check, Reference 2.12.8.*

## Gain tracking

With **GT** on, the digital trim moves opposite to any analogue gain change, so the channel level stays put. That's for when another console (or a shared rack in Receive Only) owns the preamp. On a single-console system leave it off.

Manual: [Reference 1.2.1 Channel Strip Input Area](/reference/1-2-channel-input-common-elements), [2.12.8 Socket Options](/reference/2-12-setup-menu).
