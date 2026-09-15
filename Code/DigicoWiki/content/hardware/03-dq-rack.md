# DQ-Rack (Dante stage rack)

48 mic/line inputs, 24 line outputs of which sockets 6, 12, 18 and 24 can each become a pair of AES outputs, dual redundant PSUs (two separate mains feeds), Dante primary and secondary ports, and a small LCD menu on the top panel. 19" rack, 11 kg. Only works with SD and Quantum consoles.

![DQ-Rack front](/figures/dq-p008-1.png)

## Connect it

1. Both IEC inlets powered.
2. Primary Dante port to the network (Secondary to a second switch for redundant mode; the mode is set in Dante Controller). While initialising the network field shows *Reset*.
3. Dante Controller: set the rack's sample rate to match the console and subscribe its channels to/from the DMI-Dante card. See [DMI-Dante 64@96](/hardware/02-dmi-dante-64-96).
4. Console: Audio I/O > **add port** > DQ-Rack > conform. Requires DMI firmware v103 and Dante firmware 4.0.20+ on the card.

Rack inputs 1–48 arrive as Dante channels 1–48; AES outputs use Dante channels 49–56 when enabled.

## The front-panel display

Locked by default. Hold both **left and right arrows** for 2 seconds to unlock; it relocks after 2 minutes idle. Left/right move between pages, up/down pick items, left/right change values.

Main (locked) display shows **SR** (sample rate), **Mode** (switched or redundant Dante), and **Link**: *OK* when control data is arriving from the console, *NO CTRL* when it isn't. Flashing green background = linked to a console; light blue with flashing red = not connected. The Dante device name (set in Dante Controller) shows at the top.

![DQ-Rack main display](/figures/dq-p011-2.png)

Menus: **Status** (rate, control, temperature), **Line/AES** (switch outputs 6/12/18/24; the LED under the socket goes blue in AES mode; on a Quantum this is also switchable from Audio I/O), **Oscillators** (hold right to send tone to all 24 outputs; 8 frequencies, level −96 to 0 dB), **PSU Status**, **Version** (Host, FPGA, DNT and Dante), **Display** brightness, **Default Rack** (hold right to reset everything), **Network** (primary/secondary UP or DOWN, IP addresses).

## Clock

The rack follows the Dante network clock, which follows the console via the DMI card set as Preferred Master.

## Firmware

DQ-Rack updates use the DQ & MQ Rack Updater over USB-B (TN585); the DiGiCo Dante Rack Utility does not update DQ-Racks.

Full guide: [DQ & MQ-Rack User Guide (PDF)](/downloads/digico-dq-mq-rack-user-guide-issue-a.pdf), mirrored under [DiGiCo documents](/docs/dq-1-1-introduction). Manual: [Reference 3.1.9 DQ-Rack](/reference/3-1-console-audio-connections).
