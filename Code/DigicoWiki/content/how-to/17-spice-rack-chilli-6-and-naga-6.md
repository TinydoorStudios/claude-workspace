# Spice Rack: Chilli 6 multiband and Naga 6 dynamic EQ

The Spice Rack is the Quantum processing rack. Two devices: **Chilli 6**, a multiband compressor with four flat-top bands plus two parametric bands, and **Naga 6**, a six-band dynamic EQ. You insert one on a channel or bus like any internal device, then edit it here.

![Processors > Spice Rack (Chilli 6)](/figures/q2-spice-rack.png)
*Processors > Spice Rack (Chilli 6) — Quantum 2 offline software, V22.*

Open it: Master screen > **Processors** > **Spice Rack**. Soloing a channel that has a Spice Rack unit inserted brings the rack up on the right slot automatically.

## Insert one

1. In the channel's Output panel choose **insert A** or **insert B** (or the main output).
2. Route the insert send to the **INTERNAL** port > Spice Rack slot. With **send+return** on, the return follows.
3. In the Spice Rack, the slot shows the channel name and insert. Press **type** to switch a slot between Chilli 6 and Naga 6. Two units can be **linked** for stereo.

## Controls that matter

![Spice Rack / Chilli 6](/figures/ref-p126-1.png)
*Manual figure: Spice Rack panel with controls labelled — routing, safe, link, side chain source/type, dB range, response graph, solo — SD Quantum Software Reference, Issue H, p.126.*

- **Threshold**, **attack**, **release** per band. **Release shape** goes from exponential (0) through linear (0.5) to inverse-exponential (1), which smooths sharp decays between peaks.
- **Dynamic angle** is the ratio-like control: 1 (default) is a high ratio with a hard transition, lower values soften it and start gain reduction below the threshold.
- **Gain** per band is static; **Range** limits how far the dynamics can push (blue highlight above for expansion, below for compression).
- **Crossover slope** (Chilli only) between second-order (0) and true fourth-order (1).
- **Split** mode gives a parametric band its own sidechain filter.
- **Side chain source route** picks an external key; each band chooses **Int / Ext**.
- **listen** solos one band to Solo 1, Solo 2 or both, non-destructively, unless **Destructive** is on. **Bypass** per band keeps phase; **Bypass All** is global.
- The green line on the graph is the live processed response.

## Working the controls

Two interaction modes (**faders** or **touch turn**). In touch-turn mode press a parameter and turn the Touch-Turn encoder; its button toggles bypass (rotaries) or listen (faders).

## Presets

**presets** opens the usual preset panel; factory presets are locked starting points, **new** saves the current state, **default** resets the slot. **safe** protects the unit from snapshots.

Manual: [Reference 2.6.2–2.6.5](/reference/2-6-fx-processors), [Getting Started 1.10 Spice Rack](/console/1-10-spice-rack).
