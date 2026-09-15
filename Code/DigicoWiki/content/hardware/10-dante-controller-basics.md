# Dante Controller basics (for the DQ-Rack and A168D)

Dante Controller is Audinate's free app (Mac/Windows). Run it on a laptop plugged into the DMI-Dante card's **Control** port or into the Dante switch. Everything about *which* Dante channel carries *what* is decided here, not on the console.

## The three tabs that matter

**Routing**: a grid of transmitters across the top, receivers down the side. Click a crosspoint to subscribe; a green tick means flowing. Subscribe the DMI card's receive channels 1–48 to the DQ-Rack's transmit channels 1–48, and the rack's receive channels 1–24 to the DMI card's transmit 1–24 (the rack's 4 switchable AES outs ride on Dante channels 49–56). Do the A168D the same way on the next block of DMI channels. Keep the numbering 1:1 so the console's socket names stay honest.

![Dante Controller Routing tab: transmitters across the top, receivers down the side, green ticks where a crosspoint is subscribed](/figures/dq-p019-2.png)
*Dante Controller's Routing tab — the DQ-Rack's inputs subscribed straight across to the DMI card's matching receive channels — DQ & MQ-Rack User Guide p.19.*

**Device Config** (double-click a device): sample rate (must match the console; the card's Auto SRC covers a mismatch but don't rely on it), device name, latency, and Redundant vs Switched network mode for the DQ-Rack.

**Clock Status**: exactly one device should be **Preferred Master**: the DMI-Dante card, with **Sync To External** ticked so it follows the console. Everything else unticked. Two preferred masters or an external sync on the wrong box gives you a network that argues with itself, which you hear as clicks.

![Dante Controller Device Config (sample rate) and Clock Status (Preferred Master, Sync To External)](/figures/ref-p200-1.png)
*Device Config tab (sample rate) and the Clock Status view with Preferred Master / Sync To External columns — the console-as-master setup described above — Reference Manual p.200.*

## Naming

Give devices real names (DQ-Rack-Stage, A168D-Drums). The DQ-Rack shows its Dante name on its LCD.

## Presets

Dante Controller can save the whole routing to a preset file (File > Save Preset). Save one for each venue setup once it's right, so a rebuild is a two-minute load.

## Switch settings

Dante needs a switch that doesn't block multicast or mangle QoS. The house standard for Cisco switches (IGMP snooping and querier, DSCP, EEE off) is in the [Live Sound KB Dante article](https://kb.tinydoorstudios.com/dante-cisco-switch-config).

Manual: [Reference 3.1.8](/reference/3-1-console-audio-connections), [Getting Started 2.9](/console/2-9-dmi-dante-64-96-dante-io-control), [DQ & MQ-Rack guide 1.6](/docs/dq-1-6-connecting-a-dante-rack).
