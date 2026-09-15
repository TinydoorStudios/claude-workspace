# Send inputs to a multitrack recorder (Copy Audio)

![Copy Audio — Quantum 2](/figures/q2-copy-audio.png)

You don't need a direct out per channel to record a show. **Copy Audio** duplicates any input socket to any output port (MADI, USB audio, Dante) without using console processing, and can flip the console to play the recording back for a virtual soundcheck.

## The quick way: whole rack to one port

Setup > Audio I/O > select the rack in the ports list > **Copy Audio To** dropdown > pick the destination port (e.g. USB audio / MADI to the recorder). All of that rack's inputs are copied in order.

## The matrix way: pick and choose

Setup > **Copy Audio**. Input ports run down the left, output ports across the top. Touch a port to expand its sockets; touch or drag on the grid to make routes.

![Copy Audio matrix](/figures/ref-p155-1.png)

- **Red** cell = the copy that's also the **Listen Source** for that input. The first copy you make is red.
- **Orange** cells = further copies. Any input can be copied to as many outputs as you like.
- Outputs already in use by a channel route are blue and can't be overwritten here (but channel output routes *can* overwrite copy routes, so keep the recorder port clear of bus routing).
- **move outputs / copy outputs** shift a whole set of copy routes from one output device to another. **presets** save routings.

Copy Audio settings aren't in snapshots.

## Virtual soundcheck: listen to the playback

Wire the recorder's outputs back into the console (MADI in, USB audio in). With copy routes in place, turn on **Listen to Copied Audio** and every channel whose input has a listen source flips to the recorder's playback of that socket. Turn it off and you're back on the live inputs; gain, EQ, everything else stays.

**Listen Safe** (Copy Audio panel, Channel List in Edit mode, or the channel's Setup panel) excludes a channel from the flip; its name box goes red. Use it for the talkback mic or a live feed that must stay live.

## What this looks like here

The Memo and FSQ record paths (DiGiCo USB MADI into REAPER, and the Companion one-button record chain) live on the venue pages once they're written. The console side is the above.

Manual: [Reference 2.12.9 Copy Audio](/reference/2-12-setup-menu), [Getting Started 1.4.7 (MADI recorder setup)](/console/1-4-software-configuration).
