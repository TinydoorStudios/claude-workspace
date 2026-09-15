# Audio sync and clocking

![Audio Sync — Quantum 2](/figures/q2-audio-sync.png)

Setup > **Audio Sync**. The session sample rate (48 or 96 kHz) is set in Session Structure; this panel only chooses where the clock comes from.

![Audio Sync panel](/figures/ref-p157-2.png)

Default is **Master** (internal). The Q225 can also lock to Word Clock, AES, MADI, the Waves card, and DMI cards (Dante, MADI). A green **OK** beside a source means a valid clock is present there, whether or not it's selected. The setting is saved in the session.

## What we run

- Console **Master**. Racks on MADI (MQ-Rack) and the DMI cards follow it.
- **DMI-Dante 64@96**: in Dante Controller set the DMI card to *Preferred Master* with *Sync To External* on, so the card takes clock from the console and the Dante network follows the console. The DQ-Rack and A168D lock to the network. If instead the console must follow an existing Dante network, set Sync To External **off** on the card and pick the Dante DMI as the console's sync source.
- **DMI-Waves**: either the console clocks the SoundGrid network (set in the Waves control panel: source *Digital*) or the card is the console's source.
- **MQ-Rack** normally takes clock from the console over MADI; its own menu can force Main/Aux or internal.

## Sample rate conversion

The Dante 64@96 card has **Auto SRC** in Audio I/O: it turns on by itself when the Dante network and the console differ (48 vs 96 kHz) with no loss of channel count. DMI-MADI SRC (V167+) is manual: pick 48 kHz, 96 kHz smux or 96 kHz hi-speed to match the far end; the panel shows *SRC active* or *inactive*. SRC converts between 48 and 96 on the same base clock; it will not marry two free-running systems at the same nominal rate.

## Symptoms of a clock problem

Ticks or crackle on a digital input, a rack display showing NO LOCK, a DMI card port going red in Diagnostics. Check the OK lights here first, then the Dante Controller clock status tab.

Manual: [Reference 2.12.10 Audio Sync](/reference/2-12-setup-menu), [3.1.7–3.1.8 DMI SRC and Dante 64@96](/reference/3-1-console-audio-connections), [Getting Started 1.6](/console/1-6-audio-sync).
