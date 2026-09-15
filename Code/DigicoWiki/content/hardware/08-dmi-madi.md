# DMI-MADI (BNC and Cat5e)

Two flavours: **DMI-MADI B** (BNC, AES10) and **DMI-MADI C** (DiGiCo Cat5e, which is *not* Ethernet). Either gives the console a second MADI port: a standard 64-channel MADI stream at 48 or 96 kHz, or one DiGiCo rack (D-Rack, D2-Rack, SD-Rack, SD-MiNiRack; 56 in/56 out plus control data on channel 57). One DiGiCo rack per card.

![DMI-MADI](/figures/ref-p226-1.png)

## Wiring

- Standard MADI at 48 kHz: card IN A ← device OUT, card OUT A → device IN.
- Standard MADI at 96 kHz using both ports: A carries channels 1–32, B carries 33–64.
- D2-Rack/SD-Rack: card A pair to the rack's **Main** pair; add the B pair to the rack's **Aux** pair for 96 kHz or redundancy. Console Audio Sync = Master.
- MADI-C: the two internal switches must be in the **A / Console mode** position before the card goes in (Rack mode is for the far end being a console). Two cards set to the same mode can't pass audio.

![Card A/B to rack Main/Aux](/figures/ref-p227-1.png)

## Sample rate conversion

Audio I/O > select the card port: choose **48 kHz**, **96 kHz smux** or **96 kHz hi-speed** to match the far device. No auto mode. The panel shows *SRC active* or *inactive* depending on whether the console rate differs.

## Sharing a rack with a monitor console

At 48 kHz a D2/SD/MQ rack on this card can be shared: this console on the Main pair as master, the other console on the rack's Aux MADI OUT in Receive Only with gain tracking, syncing to that MADI input. See [Conform the I/O racks](/how-to/09-conform-the-io-racks).

Manual: [Reference 6.2 DMI-MADI Cards](/reference/6-2-dmi-madi-cards), [3.1.7 MADI DMI (SRC)](/reference/3-1-console-audio-connections), [TN339](/docs/tn339-dmi-setup).
