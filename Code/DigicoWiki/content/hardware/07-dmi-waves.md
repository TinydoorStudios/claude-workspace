# DMI-Waves (SoundGrid)

64 in / 64 out at 48 or 96 kHz to a Waves SoundGrid network over Ethernet. Two ports that act as a small switch: one to the computer running SuperRack SoundGrid, the other to a SoundGrid server or another I/O, so a two-device system needs no switch. Link/Activity LED flashes green, GigE LED solid orange. Bigger systems use a Waves-approved 1 Gb switch in a star.

![DMI-Waves](/figures/ref-p236-1.png)

There is **no control from the console**: the card is just 64 sockets each way in Audio I/O. Everything else happens in Waves software on the host computer. The console cannot run Waves software itself.

## Plugins via SuperRack

1. Console: Options > **Console** > *Enable External Waves* = Yes, pick the console network port, choose **ProLink** (needs SuperRack SoundGrid 14.30+; *Legacy* is the old remote mode). Power cycle the console.
2. SuperRack: Controllers pane > add **ProLink Console Remote** (remove *Legacy Console Remote* if present), tick **Assign** until it says *Connected*. The network port is picked automatically.
3. Route a channel insert send to the DMI-Waves port and the return from it (mono > mono or mono > stereo for mono channels into stereo racks). Build the rack in SuperRack on the matching I/O channels.

With ProLink, saving or loading a session on the console loads the same-named SuperRack session from its Integrated Sessions folder (Windows: `C:\Users\Public\Waves Audio\SuperRack SoundGrid\Integrated Sessions`; Mac: `/Users/Shared/Waves Audio/SuperRack SoundGrid/Integrated Sessions`). Global tempo and unattended mode sync too. Fourier and Waves integration can't both be on.

## Clock

Waves control panel (gear on the device in the SoundGrid rack, or the driver control panel) > **Clock** page: **Digital** = the card follows the console; **Sync over Ethernet** = follows the SoundGrid master; **Internal** = the card is master and the console can select the Waves card in Audio Sync. Firmware status is the FW button colour: grey OK, blue update available, red must update.

## As a recorder interface

The same card feeds a SoundGrid ASIO/Core Audio driver on the host, so a DAW on the SuperRack computer can record the 64 channels; patch the driver in the SoundGrid host's setup. Copy Audio to the Waves port works for this (see [Copy Audio](/how-to/28-copy-audio-to-a-recorder)).

Guide: [DMI-Waves user guide (PDF)](/downloads/dmi-waves-user-guide-v2.pdf), mirrored at [DMI-Waves User Guide](/docs/dmi-waves-guide). Manual: [Reference 6.5](/reference/6-5-dmi-waves-hydra-cards), [2.5.9 Options > Console](/reference/2-5-options).
