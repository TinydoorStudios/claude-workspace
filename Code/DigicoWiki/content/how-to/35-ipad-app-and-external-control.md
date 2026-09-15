# iPad app, OSC and other external control

Setup > **External Control** is the one panel for everything that talks to the console over the network: the DiGiCo iPad app, generic OSC devices (Companion, TouchOSC), KLANG, Sound Devices Astral, L-ISA, Soundscape, Spacemap and LiveTrax.

![Setup > External Control](/figures/q2-external-control.png)
*Setup > External Control — Quantum 2 offline software, V22.*

Turn **Enable External Control** on only while you need it; DiGiCo asks you to switch it off otherwise.

## DiGiCo iPad app

1. Enable External Control.
2. **Add Device** > **DiGiCo Pad**. Name it, enter the iPad's IP, and Send/Receive ports (e.g. 9000 / 8000; each device needs its own pair).
3. Tick **Enabled**.
4. First time only: **Load** the command set for the Quantum 225. Only one command set should be loaded; if unsure, **Clear All** and reload.
5. Note the console's **Local IP** at the bottom of the panel; enter it in the app's Connect page.

![External Control: iPad](/figures/ref-p173-1.png)

## Generic OSC (Companion, TouchOSC)

Add Device > **Generic OSC Device**, Input Channel Controller = *OSC Generic*, choose *Other OSC*, enter name, IP, send/receive ports, tick Enabled. **Customise** defines 8 rotaries and 8 switches with label, OSC address, min/max/default; the address uses `*` for the channel number (`/MyDevice/MyParameter/*`).

To *send* OSC from the console, define a **Macro OSC** device here and use the MacroOSC command type in a macro (see [Macros](/how-to/25-macros)). *Suppress OSC retransmit* stops the same message repeating; *Bundles* sends OSC bundles.

## KLANG

Add Device > **KLANG**, IP 192.168.1.200 (the card's default fixed IP), send 9111 / receive 8200, tick Enabled; the connection status goes green. Full setup on the [DMI-KLANG](/hardware/06-dmi-klang) page.

## Sound Devices Astral (V20+)

Add Device > Astral, enter the Nexus IP (ports are fixed), enable. On the Nexus enter the console IP and a Device ID (up to 5 redundant pairs or 15 single boxes). Macros on the A20 transmitters then fire console macros by Device and Command ID. V22 adds RF, battery and audio monitoring on the console.

## LiveTrax 3 (V22)

External Control > **Integration** > LiveTrax: with *Send Snapshot Markers* on, firing a snapshot while LiveTrax records drops a named section; when not recording, firing a snapshot locates playback to that section. LiveTrax itself needs the DiGiCo control surface enabled with the console IP and receive port; *Create session from console* builds tracks with the console's channel names.

Manual: [Reference 2.13 External Control](/reference/2-13-external-control), [V22 release notes 1.5–1.6](/docs/v22-release-notes).
