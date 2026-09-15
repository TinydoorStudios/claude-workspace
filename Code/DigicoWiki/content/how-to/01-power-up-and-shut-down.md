# Power up and shut down

Everything else on this wiki assumes the desk is up. Here's the order that keeps it happy.

## Power up

1. Make all audio and network connections first: MADI/Dante to the racks, Ethernet to the KLANG/Waves computers, USB MADI to the recording machine. DiGiCo's advice is connections before power, every time.
2. Turn on both rack power supplies (DQ-Rack / MQ-Rack). Both PSUs stay on all the time; they're redundant, not "main and spare".
3. Turn on both console PSUs (rear panel). The console boots straight into the Quantum 2 software and comes back exactly as it was when it was last shut down, including the session that was loaded.
4. Wait for the Master screen. If the desk has been asked to autoload a startup session (Options > Console > *Load startup session*), that happens now.

![Rear panel: dual PSU, DMI slots, MADI, Ethernet, GPIO](/figures/gs-p008-1.png)
*Manual figure: rear panel connections, Getting Started 1.2.*

![The Master screen on the Q225 (offline software, V22)](/figures/q2-master-screen.png)
*The Master screen on the Q225 — Quantum 2 offline software, V22.*

## Shut down

Never just kill the power. The console PC is a Windows machine and the session in memory is only as safe as your last save.

1. Save the session if anything changed (Files > **Save Session**, or Save As New File if you want to keep the previous version).
2. Master screen > **System** > **Shutdown**. If the session isn't saved you get a warning: *Yes* shuts down without saving, *No* cancels so you can save first.
3. Wait for the message saying it's safe to switch off, then turn off the console PSUs.
4. Racks last, if you're powering them down at all.

![System menu](/figures/q2-m-system.png)
*System menu — Quantum 2 offline software, V22.*

*Reset Computer* in the same menu reboots the control PC without touching the audio engine. *Quit to Windows/Home* drops you to Quantum Home, which is where display and network settings live.

## If the desk is powered but the surface is dead

System > **F12: Reset Surfaces** restarts every worksurface control. It briefly interrupts audio on the Local I/O only. See [Troubleshooting](/how-to/33-troubleshooting) for the other resets.

Manual: [Getting Started 1.3 Hardware Configuration](/console/1-3-hardware-configuration), [Reference 2.1 System Menu](/reference/2-1-system-menu).
