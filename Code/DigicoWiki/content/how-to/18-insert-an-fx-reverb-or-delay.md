# Add a reverb or delay (internal FX)

![Fx — Quantum 2](/figures/q2-fx.png)

The console's own FX are stereo FPGA reverbs, delays, chorus, pitch and enhancers, created from **fx presets** and fed from any channel output, direct out, aux or insert send.

## The usual way: an aux feeding a reverb

1. Pick an aux to be the reverb send. Touch the **bottom** of the aux strip to open its Output panel and press **fx presets**.
2. Choose a preset (factory ones have a red padlock). The FX unit is created and the aux's output is routed into it.
3. The FX **return** comes back on a channel: route an input channel's input to **INTERNAL** > the FX unit's outputs. Route that channel to the master as normal.

On any output channel the **FX Output** button under the meters reopens the unit's controls; on an input channel touch the **pan area** once an FX preset is on its direct out.

![Master FX panel](/figures/ref-p124-1.png)

## The FX rack

Master screen > **fx** shows every unit in one rack. **New** (top left) creates one from the presets list; to delete a unit press its **fx presets** button and deselect the preset. Every unit has a **safe** button and shows its input/output meters and which channel feeds it. Touch any control to put it on the Touch-Turn encoder. Reverbs also have a graphical editor: the coloured sliders on the graph are the unit's rotaries.

## Tap tempo

Delays can join a **global tap**: press the tap button on the unit to cycle through off, ×0.25, ×0.5, ×1, ×2, ×3, ×4. A macro command type *Global Tap Tempo* sets the tap from a smart key; you can also type the value with the keypad icon on the delay panel.

## Killing tails

System > **F10: Reset FX** clears every reverb and delay tail at once (all FX are briefly bypassed).

## Saving your own presets

Adjust a unit, then in the fx Presets panel save as a new preset or update an existing unlocked one. With **edit name** on, touching the lock column locks or unlocks a preset. Presets travel with the session and can be exported with Files > Save Presets.

Manual: [Reference 2.6.1 The Master FX Display](/reference/2-6-fx-processors), [1.3.4 FX Presets](/reference/1-3-channel-output-and-inserts-common-elements).
