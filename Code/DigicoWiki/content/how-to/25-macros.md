# Macros and smart keys

![Macros — Quantum 2](/figures/q2-macros.png)

A macro is a list of console commands fired from a smart key, a keyboard F-key, a GPI, an OSC message, a snapshot, a fader or meter condition, or just by touching it in the list.

Setup > **Macros** (or the **assign** button in the macros area of the surface) opens the list of every macro with its trigger.

![Macros panel](/figures/ref-p160-1.png)

## Make one

1. Press **new** (or **duplicate** an existing one). The Macro Editor opens with the name "macro n"; touch the name to rename it. A comma in the name makes a line break on the smart key.
2. Add commands, two ways:
   - **capture** (top right): press it, do the moves on the console, press it again. Everything you touched is listed in order.
   - or pick a **command type** on the left, then a command from the list below (search box at the top; V22 filters the types as you type). Set the channel range and value.
3. Commands run in list order. Touch a row to insert before it.

![Macro Editor](/figures/ref-p162-1.png)

## Trigger it

The editor's trigger tabs (V19+): **Smart Keys** (bank, button, on/off action, colour), **External** (GPI, OSC, MIDI program change), **Snapshots** (one or more snapshots fire it; a snapshot can only trigger one macro), **Other** (F keys, audio mastership switch, prev/next snapshot buttons), **Advanced** (fader above/below a level, mute or solo state, meter level incl. *signal present*, on any/all of a list of channels).

From the main Macros panel, **assign** > touch the macro > press the smart key is the quick route. **Transport** fills the macro buttons with transport controls. **delete files** with select all / select range removes macros.

## Sending OSC

A **MacroOSC** command type transmits an OSC message (integer, float, string or address-only) to a *Macro OSC* device defined in Setup > External Control (IP and send port). This is how the console talks to Companion, lighting or the recorder.

## Useful ones from V22

*Lock Console* (jump to Live or Unattended security mode), *Switch to Bank*, *Global Tap Tempo*, LiveTrax record/navigation, *Update Current Snapshot*, *Clear Master Screen*. Macros can now be reordered with **move**.

Manual: [Reference 2.12.12–2.12.14 Macros](/reference/2-12-setup-menu).
