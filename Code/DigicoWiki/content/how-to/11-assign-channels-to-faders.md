# Put channels on faders (layers, banks, assign, swap)

The Q225 surface is two sections of 12 faders. Each section has up to 3 **layers**, each layer up to 4 **banks** of 12. The bank and layer buttons sit to the right of each section. Hold a bank button on one side and press the other side's to switch both sections together.

![One bank of twelve input channels on the Left screen](/figures/q2-channel-strip.png)
*One bank of twelve input channels on the Left screen — Quantum 2 offline software, V22.*

![Layout > Fader Banks](/figures/q2-fader-banks.png)
*Layout > Fader Banks — Quantum 2 offline software, V22.*

![Layout > Channel List](/figures/q2-channel-list.png)
*Layout > Channel List — Quantum 2 offline software, V22.*

![Layers and banks](/figures/gs-p009-1.png)

Default layout: inputs on layer 1, outputs (groups, auxes, matrices) on layer 2, control groups on layer 2 as well. The right section can also show the Master screen (button above the master fader).

## Assign a channel to a fader

1. Select the bank you want to fill.
2. Press the section's **LCD Function** button. The LCDs turn yellow and list the functions.
3. Press **ASSIGN FADERS**. LCDs go dark green and read ASSIGN.
4. Press the LCD/select button of every fader slot you want to fill.
5. Layout > **Channel List** opens (or open it). Expand the channel type and touch the first channel. The selected slots fill in ascending order from the lowest one you pressed.

![Assign faders](/figures/ref-p061-1.png)

Other LCD functions on the same menu: **UNASSIGN FADERS** (blank a slot), **SWAP FADERS** (press two), **MOVE FADERS** (shift right one place), **COPY BNK FROM / TO**, **CLEAR BANK**. None of these have undo.

The LCD menu auto-reverts to Solo after a timeout if Options > Surface > *Auto-revert LCD menu to solo* is on.

## Move whole banks around

Layout > **Fader Banks** shows every bank position on both sections. Highlight a bank, then **swap**, **move**, **copy to**, **clear**, or **lock** (a locked bank can't be cleared by accident). The bank LCD label and colour are editable at the bottom. The master fader can be reassigned here too (*Assign master fader*).

![Fader Banks panel](/figures/ref-p083-1.png)

## After a restructure

New channels don't appear on the surface unless you restructured with **Rebuild Banks** on. Either rebuild (loses your custom layout) or assign them by hand as above.

## Spill sets

Layout > **Set Spill** lets you define sets of channels from anywhere on the desk and spill them onto the surface together, from the panel or from a macro. Control Groups can spill their members directly with the **Spill** button on the CG strip.

Manual: [Reference 1.8 LCD Functions](/reference/1-8-lcd-functions), [2.3 Layout Menu](/reference/2-3-layout-menu), [Getting Started 1.2.2 Layers and Banks](/console/1-2-before-you-start).
