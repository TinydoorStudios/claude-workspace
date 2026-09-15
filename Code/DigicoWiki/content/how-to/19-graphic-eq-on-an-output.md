# Put a graphic EQ on an output

The console has a bank of 32-band graphic EQs. They're internal devices, inserted on a bus like an FX unit.

![Graphic EQ panel](/figures/q2-graphic-eq.png)
*Graphic EQ panel — Quantum 2 offline software, V22.*

## Insert it

1. Open the bus's Output panel (touch the bottom of the strip). Choose **insert A** or **insert B**.
2. Turn **send+return** on, route the insert send to **INTERNAL** > Graphic EQ n. The return is set automatically.
3. Switch the insert **on** in the strip (button goes red).

A stereo bus takes two graphics; they're ganged automatically when inserted on a stereo or surround channel.

## Edit it

Master screen > **Graphic EQ**. Touch any of the miniature EQs to bring it into the expanded view at the bottom. The 32 faders are on the surface faders while the panel is open; gain trim pot, **on** (ringed red) and in/out meters are on the left.

![Graphic EQ panel](/figures/ref-p137-1.png)
*Manual figure: Graphic EQ panel — miniature EQs and one expanded — SD Quantum Software Reference, Issue H, p.137.*

- **GANG / build gang**: press build gang on one EQ, then touch other miniature EQs to add them. Ganged EQs move relatively. Hold a band's mute button while moving it to isolate that band from the gang for one move.
- **all** makes every EQ jump to the band you move (absolute, so differences between EQs vanish).
- **flat** zeroes all 32 bands (and any ganged EQs).
- **safe** protects it from snapshots. **preset** saves and recalls; **default** resets.

Soloing a bus with a graphic on its insert can pop the Graphic EQ panel automatically — it's gated by Options > Solo > *Solo Displays Inserts and Outputs* (on by default), and the panel itself only shows on the Master screen.

Manual: [Reference 2.8 Graphic EQ Panel](/reference/2-8-graphic-eq-panel).
