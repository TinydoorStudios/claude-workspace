# Start a new session (templates and Session Structure)

![Templates — Quantum 2](/figures/q2-templates.png)

Don't build from nothing on show day. Load the house template, then rename and save it as the show. Building from scratch is for when the channel count or bus layout has to change.

## From a template

Files > **Templates** > pick the template > **Load**. Then Files > Save As New File with the show name.

## Session Structure (when you need a different layout)

Files > **Session Structure** is where the session gets its name, sample rate and channel allocation. Nothing changes until you press **Restructure**.

![Session Structure](/figures/ref-p073-1.png)

- Sample rate at the top: 48 kHz or 96 kHz.
- Session title box.
- One row per channel type: input channels, mono/stereo aux busses, mono/stereo group busses, matrix ins and outs, control groups. Touch a count box and type a number.
- The Q225 has 72 input channels and 36 busses (plus the master, stereo or LCR) to split between those rows. The bottom of the panel shows how much processing is still unallocated.
- **Aux Order / Group Order** let you interleave mono and stereo busses instead of the default "all mono, then all stereo".

Three buttons matter:

- **Clear All** (per row) wipes non-default routing and processing from that channel type when you restructure. Use it when you're making a genuinely new session.
- **Auto-route** (only with Clear All) patches Port 1's physical inputs to input channels in order, and aux/group/matrix outputs to physical outputs in order. It overwrites existing routing.
- **Rebuild Banks** (horizontal or vertical) lays every channel out on the surface again. Without it, new channels exist but aren't on any fader; see [Assign channels to faders](/how-to/11-assign-channels-to-faders).

Also here: *clear snapshots*, *clear macros*, the global send point for direct outs and aux sends (post-fader / pre-fader / pre-mute), and **Default All**, which builds a plain session with rack 1 into the inputs and the master on Local 1+2.

Press **Restructure** to apply, **Cancel** to leave, **REVERT** (top left) to throw away unapplied edits. A Save panel usually appears after a restructure; give it a new name.

Manual: [Reference 2.2.2 Session Structure](/reference/2-2-files-menu), [Getting Started 1.4 Software Configuration](/console/1-4-software-configuration).
