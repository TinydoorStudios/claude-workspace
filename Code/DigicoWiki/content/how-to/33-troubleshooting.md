# Troubleshooting

Work top-down. Most "no audio" calls are routing or a mute, not a fault.

![System > Diagnostics](/figures/q2-diagnostics.png)
*System > Diagnostics — Quantum 2 offline software, V22.*

## No audio on a channel

1. Is the channel **muted**, CG-muted (blue CG MUTE indicator) or hard-muted? Is the fader up? Is the **main/alt** input the one you expect (red = alt)?
2. Channel Setup: is an input actually routed? Does the input **meter** move? If not, check the socket in Audio I/O: gain, 48V for a condenser, the card label green.
3. Output panel: is the channel routed to the master (or the group that feeds it)? Is the group routed to a physical output?
4. Is the aux/group **on** and routed? Check *Grp:* and *Dir:* under the channel name.

## Nothing from the whole desk

- **Status** display (Options > Status, or the Master screen status bar): red = look there.
- System > **Diagnostics**: engine, surfaces, DMI cards, network. On the **Engine** tab you'll also see Mustard and nodal counts.
- Racks: MQ-Rack display should flash green when linked, *LOCK* on the main display; DQ-Rack *Link: OK*. Light blue with red = not connected to a console.
- Audio Sync: does the selected source show green **OK**?

## Clicks, crackle, pitch drift

Clocking. See [Audio sync and clocking](/how-to/27-audio-sync-and-clocking). Two clock masters on the Dante network, or a DMI-MADI SRC set to the wrong rate, are the usual culprits.

## Faders, screens or buttons stop responding but audio is fine

System > **F12: Reset Surfaces**. Brief audio interruption on the Local I/O only.

## FX stuck, reverb won't stop

System > **F10: Reset FX**. Briefly bypasses all FX.

## Engine

System > **F11: Reset Engine** restarts the audio engine. Audio drops for the duration. Last resort short of a reboot. **Restart Computer** reboots the control PC without touching the engine.

## Session won't load / behaves oddly

Check the console software version against the session (V22 opens older files). Try **Partial Load** to pull only the channels. In V22, sessions corrupted by setlists are recovered on load.

## Clip lights

System > **Signal Over Indicators** lists every over; touching one brings the channel up. *Clear Over Indicators* resets them. Options > Status can make the panel open automatically.

## Collect logs for DiGiCo (V22)

System > Diagnostics > **Console** > **Collect Diagnostics**. Choose D:\logs or a USB drive, tick *include session file*, press **Start**. It writes a `.ddr` file; email it to support@digiconsoles.com with a description. (Not available in the offline software.)

## Startup files

If the desk boots into a bad session, Quantum Home (System > Quit to Home) > Settings > **Delete Startup Sessions** removes `startup.ses` and `_session.ses`. Holding **Space** during boot goes to Quantum Home without launching the console app.

Manual: [Reference 2.1 System Menu](/reference/2-1-system-menu), [2.5.10 Options > Status](/reference/2-5-options), [5.1 Quantum Home](/reference/5-1-quantum-home), [V22 release notes 1.9](/docs/v22-release-notes).
