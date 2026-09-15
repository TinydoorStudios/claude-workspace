# Copy channel settings, and use presets

## Copy To / Copy From

![Copy To panel](/figures/q2-copy-to.png)
*Copy To panel — Quantum 2 offline software, V22.*

![Channel Presets](/figures/q2-channel-presets.png)
*Channel Presets — Quantum 2 offline software, V22.*

In Channel Setup (top of the strip) the **Channel Settings** area has **Copy To** and **Copy From**.

- **Copy To** takes *this* channel and pastes it onto one or many others. Press Copy To, tick the scope buttons (input, EQ, dynamics, aux sends, outputs… they go pink when included), then press the select button of each destination. **Stay Open** keeps the panel up while you hit several destinations.
- **Copy From** pulls settings *into* this channel (and the ones to its right) from a source channel. Set how many channels to copy with the numbered buttons, then press the select button of the left-most source.
- **undo previous copy** is on the panel if you get it backwards.

![Copy channels](/figures/ref-p017-3.png)
*Manual figure: Channel Settings area (Copy From/Copy To) and the Copy Channels display — SD Quantum Software Reference, Issue H, p.17.*

Tip from the manual: Copy To for one-to-many, Copy From for a block-to-block.

The EQ, dynamics and Mustard panels each have their own **copy to** that only carries that module. Nodal processing has copy to/from as well.

## Channel presets

**Presets** (under the copy buttons in Channel Setup; also in EQ/dynamics panels) opens the Presets display: groups on the left, presets in the group on the right, with channel count, date and lock status.

- **Recall**: pick the group, touch the preset. The **recall scope** buttons at the bottom choose which parts come in. Opening presets from inside the EQ panel scopes it to EQ only by default.
- **Save**: choose a group, press **new**, name it, set how many channels it should capture (more than one takes the channels to the right too).
- **update** overwrites an existing preset; press update *before* touching the preset or you'll recall it instead.
- **new group**, **edit name** (rename, and lock/unlock with the padlock column), **delete** with select range / select all.

Presets are saved inside the session and can be exported/imported as `.pre` files with Files > **Save Presets** / **Load Presets**. FX, graphic EQ and matrix presets work the same way.

## Global Set to Defaults

Files > **Global Set to Defaults** applies one action to every channel of a type (e.g. all groups off, all blends LR). Undo only works while the panel is open.

Manual: [Reference 1.2.6 Copy Channels](/reference/1-2-channel-input-common-elements), [1.2.7 Channel Presets](/reference/1-2-channel-input-common-elements), [2.2.6–2.2.8 Files](/reference/2-2-files-menu).
