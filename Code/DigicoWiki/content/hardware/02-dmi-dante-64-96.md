# DMI-Dante 64@96

64 channels in and 64 out to a Dante network at 48 kHz or 96 kHz, with sample rate conversion. Two EtherCON ports (Primary, Secondary) for the Dante network and an RJ45 **Control** port for a laptop running Dante Controller. Two hardware generations exist: the original Summit HC module (green PCB) and the current **Zynq** module (black); the Zynq version takes firmware updates through a web browser at the card's IP.

![DMI-Dante 64@96](/figures/ref-p232-1.png)

## How the console sees it

Setup > Audio I/O lists the card as a port with 64 inputs and 64 outputs. The console has no idea *which* Dante device is on channel 12; that's decided in **Dante Controller** on a separate computer. The manual's own words: the Dante controller is "the critical component in determining where the audio is going to/from".

The logical setup, and the one to keep to: route rack input socket *n* to DMI channel *n*, and DMI output *n* to rack output socket *n*. Then "DMI Dante 1" on the console means "DQ-Rack Mic 1" and nobody has to think.

![Dante Controller routing: rack inputs to DMI channels](/figures/ref-p199-1.png)

## Set up from scratch

1. Card in slot, Primary port to the Dante switch (or straight to the rack), Control port to the laptop.
2. Dante Controller > **Device Config** for the DMI card: sample rate to match the console (48 or 96 kHz). Same for the DQ-Rack / A168D.
3. Dante Controller > **Clock Status**: DMI card = **Preferred Master** and **Sync To External** on. The card takes clock from the console and the network follows. Console Audio Sync stays on Master. (If the network must be master instead, Sync To External off on the card and select the Dante DMI as the console's sync source.)
4. Dante Controller > **Routing**: subscribe DMI receive channels 1–48 to the DQ-Rack transmit channels 1–48, and the rack's receive channels to the DMI transmit channels. DQ-Rack AES outputs, when active, are on Dante channels 49–56.
5. Console: Setup > Audio I/O > **add port** > DQ-Rack (or A168D) and **conform**. Gain, 48V and pad control now works from the channel strip.

![Clock status: Preferred Master + Sync To External](/figures/ref-p200-1.png)

## Auto SRC

In Audio I/O, the card's port has an **Auto SRC** toggle. On, the card converts automatically when the Dante network runs at a different rate from the console (48 vs 96). Channel count doesn't change. The panel shows both rates and the SRC state.

![Auto SRC in Audio I/O](/figures/ref-p198-1.png)

## Firmware notes (from DiGiCo tech notes)

- Controlling a DQ-Rack or A168D needs DMI firmware v103+ and Dante firmware 4.0.20 (Summit) or 4.2.x (Zynq); A168D/A164D racks themselves need DiGiCo firmware V1.5+, updated with the DiGiCo Dante Rack Utility (TN515).
- The Zynq card ships with v105 and is updated via browser at its IP (TN580/TN582; current guide: "DMI-Dante64@96 with IP Zynq HC – Upgrading firmware to v4.2.11" on support.digico.biz).
- Redundant mode (Primary + Secondary on separate switches) is set in Dante Controller, not on the console.

## Data sheet

[DMI-Dante 64@96 data sheet (PDF)](/downloads/digico-dmi-dante64at96-data-sheet.pdf).

Manual: [Reference 6.3 DMI-Dante Cards](/reference/6-3-dmi-dante-cards), [3.1.8 Dante 64@96](/reference/3-1-console-audio-connections), [Getting Started 2.9](/console/2-9-dmi-dante-64-96-dante-io-control).
