# MQ-Rack (MADI stage rack)

The MADI twin of the DQ-Rack: 48 mic/line inputs, 24 outputs (6, 12, 18, 24 switchable to AES pairs), dual PSUs, and a MADI pod with **Main** and **Aux** BNC in/out pairs. Connects to the console's own MADI port or a DMI-MADI card.

![MQ-Rack front](/figures/dq-p008-2.png)

## Connect it

Console MADI **OUT** to rack MADI **IN Main**; console MADI **IN** to rack MADI **OUT Main**. At 96 kHz, or for a redundant link, add the Aux pair the same way. Console Audio Sync = Master; the rack locks to the incoming MADI.

![MADI connection](/figures/dq-p021-1.png)

Then Audio I/O > select the port > device type **MQ-Rack** > conform. 48 inputs and 24 outputs appear; the Line Out/AES switch for the four dual sockets is on the socket in Audio I/O, and inactive outputs are greyed out in routing.

![MQ-Rack in Audio I/O](/figures/ref-p205-1.png)

## Sharing with a second console

At 48 kHz an MQ-Rack can feed two consoles: the **master** console on the Main pair with full control of gains; the second console on the **Aux** MADI OUT only, in *Receive Only* with gain tracking on, and Audio Sync set to the MADI input from the rack. Only the master console can use the rack's outputs. Details in [Conform the I/O racks](/how-to/09-conform-the-io-racks) and the manual's rack-sharing section.

## The front-panel display

Same menu system as the DQ-Rack (hold left+right 2 s to unlock). Main display: **Link**, **96k/48k**, **S** (sync source), **Outs** (which MADI input owns the outputs), **Lock** / **NO LOCK** on the incoming MADI clock.

MQ-only menus: **MADI Sync** (Auto with Main/Aux priority, or force Main/Aux; shows Active and Lock), **Out Routing** (which MADI input drives the 24 physical outputs), **Internal SR** (48/96 k, only used when syncing internally).

Data sheet: [MQ-Rack (PDF)](/downloads/digico-mq-rack-data-sheet.pdf). Full guide: [DQ & MQ-Rack User Guide (PDF)](/downloads/digico-dq-mq-rack-user-guide-issue-a.pdf). Manual: [Reference 3.1.10 MQ-Rack](/reference/3-1-console-audio-connections).
