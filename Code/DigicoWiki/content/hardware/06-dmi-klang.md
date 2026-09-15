# DMI-KLANG (immersive IEM mixing in the console)

The DMI-KLANG takes 64 channels from the console and returns **16 stereo mixes** (as 32 channels) plus a stereo engineer cue (channels 33/34). No audio connectors on the card: the audio moves over the DMI bus. Two EtherCON and one RJ45 **control** ports (all one internal switch) for the console, the KLANG:app computer and Wi-Fi for the musicians' phones; a USB port for updates and presets.

![Setup > External Control, where KLANG is added](/figures/q2-external-control.png)
*Setup > External Control, where KLANG is added — Quantum 2 offline software, V22.*

![DMI-KLANG](/figures/ref-p242-1.png)

## Install and network

- Fit it in **DMI slot 2** (KLANG say slot 1 can have degraded communication). Power off first. Never select the KLANG card as the console clock source.
- Connect the card's **Console** port to the console's network port.
- Press the card's reset button **three times quickly** to set the fixed IP **192.168.1.200 / 16**, which sits in the DiGiCo default subnet (console 192.168.x.x /16). Otherwise it uses DHCP or falls back to 169.254.x.x. The card's own control panel in Audio I/O shows Dynamic vs Fixed IP.

## Console side

1. Setup > Audio I/O > select the DMI-KLANG port, **conform**. Name the sockets: mix returns **KLANG 1**… (32 sockets for 16 stereo mixes, use auto-name), sends **KLANG 1**… ×64. Cascaded processors use *KLANG(1) n* / *KLANG(2) n*.
2. Setup > External Control > **Enable External Control: Yes**; turn on **Suppress OSC retransmit**; set **KLANG Interface: KLANG enabled**; **add device** > KLANG, IP 192.168.1.200, send 9111 / receive 8200; tick Enabled. The KLANG status goes green.
3. Route channel **direct outs** to the KLANG sockets (Layout > Channel List > Edit > outputs column > direct outs > KLANG port). Groups can go too.
4. Route each aux's **merge input** from the KLANG mix returns (Channel List > Aux Output > alt input > Merge Input > KLANG n). Auxes must be **stereo** and merge input on.
5. External Control > KLANG Interface > **Enable Mapped Channels**. Aux nodes whose sockets are named KLANG 1… become KLANG nodes.
6. Fire a snapshot, then **Enable all channels** (macro available) and **Import Levels / Pans**: the aux mix becomes the starting KLANG mix, sounding the same. Update the snapshot.

![KLANG control in External Control](/figures/ref-p179-1.png)

## Mixing

On a KLANG-enabled aux node the expanded panel shows the **orbit** (position), azimuth, elevation, type (mono/stereo/3D), level, on/off and a solo. V22 hides the pickoff point on KLANG nodes. **copy to KLANG** in the aux setup copies aux send levels to KLANG levels. Musicians use KLANG:app on a phone or tablet on the control network (CONFIG > CONNECT > pick the processor).

Interface options: **KLANG bypassed** falls back to the console's own aux mix (levels forced to 0 dB when bypassed off / −∞ when on); **Copy KLANG to Aux Send** one-way copies levels; **Recall with Session** resends everything on load.

## Modes

Stand-alone (no computer, automatic mapping, KOS 5.5+) is what the steps above give you. The app-based modes add manual mapping and cascading. KLANG's own guide covers them: [klang.com/manuals/digico](https://www.klang.com/manuals/digico/), quick start at [klang.com/manuals/dmi-klang-quick-start-guide](https://www.klang.com/manuals/dmi-klang-quick-start-guide/), firmware at klang.com/downloads.

Manual: [Reference 6.8 DMI KLANG](/reference/6-8-dmi-klang), [1.4.11 KLANG Nodes](/reference/1-4-input-channel-specific-functions), [2.13.5 KLANG Control](/reference/2-13-external-control).
