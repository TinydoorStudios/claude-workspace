# Conform the I/O racks (Audio I/O)

![Audio Io — Quantum 2](/figures/q2-audio-io.png)

"Conforming" makes the on-screen rack match the cards physically in it. If a card label under the rack graphic is **red**, the console thinks a different card is there and audio on that card is suspect. **Green** is good.

![Audio I/O panel](/figures/ref-p150-2.png)

## Conform everything

1. Setup > **Audio I/O**.
2. Press **Conform All Ports** (bottom left). The console interrogates every port and selects the right card type for every slot.
3. Check every card label turned green.

To conform only one rack: select it in the ports list and press **conform rack** under the graphic. For one card: touch a socket on it, press **Cards & Sockets**, then **conform card**.

## Ports

The list top-left has one entry per physical connection: Local I/O, each MADI rack, each DMI card, USB audio. **add port** creates a port from the drop-down of known devices (DQ-Rack, MQ-Rack, A168D, KLANG konductor, 4REA4…); **remove port** deletes one you made. The Local I/O port is fixed.

## Port control: shared racks

**Port Control** (Splits and Sharing) sets how much say this console has over a rack's gains, pads and phantom:

| Mode | What it means |
|---|---|
| **isolate** | No control data either way. Console can't change the rack and won't follow it. |
| **receive only** | Console follows the rack's settings but can't change them. This is the mode for a monitor console that tracks FOH gain. |
| **full control** | Console owns the rack. Only one console can. |

Press **Shared** for the rack, then one of the three. Going into full control warns you that live audio may change (the rack jumps to this session's settings); going into receive only warns that the session will change to match the rack.

![Port control](/figures/ref-p152-1.png)

## Standard MADI names

For a plain MADI device (not a DiGiCo rack) you can label the port with generic names, MADI 1 to 64, instead of rack-style names. It only changes labels.

## Dante racks

DQ-Rack and A168D conform the same way, but which rack socket lands on which DMI channel is decided in **Dante Controller**, not here. See [DMI-Dante 64@96](/hardware/02-dmi-dante-64-96).

Manual: [Reference 2.12.1–2.12.6 Audio I/O](/reference/2-12-setup-menu), [Getting Started 1.4.6 Automatic Conforming](/console/1-4-software-configuration).
