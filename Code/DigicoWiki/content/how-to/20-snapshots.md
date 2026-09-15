# Snapshots: store, recall, scope, safe, setlists

A snapshot is a picture of the whole console. What it *changes* when you fire it is limited by the **Global Scope**, each snapshot's own **Recall Scope**, and the **safes** on individual channels.

![Snapshots panel](/figures/ref-p092-2.png)

## Store

Master screen > **Snapshots**. Press **Insert New** to add a snapshot after the selected (green) one; name it on the keyboard. **Duplicate** copies the selected one. **Update Current** overwrites the last-fired snapshot with the desk as it is now; **Update Selected** and **Update Group** do what they say. The current snapshot isn't necessarily the highlighted one, so look at the *Current* indicator before you update.

## Recall

Three ways: **Touch to Fire** on the panel then touch the snapshot; the **previous / next** buttons on the surface (they follow the list order); or the worksurface **fire** button with the snapshot selected. **Undo** fires a hidden snapshot taken just before the last recall.

## Limit what a snapshot changes

- **Global scope** (Snapshots panel > Global Scope): a grid of channel types against controller types. Anything not ticked is never recalled by any snapshot. The house habit is to keep system-tuning items (master bus inserts, matrix, graphics) out of scope.
- **Recall scope** per snapshot: the same grid, per snapshot. Edit it for one snapshot or a range.
- **Channel safes**: Channel Setup > Safes, or the **safe** buttons in the EQ, dynamics and Mustard panels. Safed elements turn red and the channel name gets a red background. Safes only apply to snapshot recalls, not to copy/preset functions.
- Control groups, matrix, graphic EQs, FX and Spice Rack units all have their own **safe** buttons.

![Global recall scope](/figures/ref-p099-1.png)

## Edit several snapshots at once

Press **Edit Range**, select snapshots (pressing them now selects instead of firing), make the change on the desk; only that change is written to the selected snapshots. Deselect Edit Range when done.

## Housekeeping

**Move** (touch to select in V22, then choose before/after the destination), **Rename**, **Renumber** (a range), **Delete** (select range or all, then confirm), **Notes** per snapshot, **Lock** to stop a snapshot being updated.

## Recall times and crossfades

Each snapshot can carry a timecode recall time (capture on insert, or *Update recall time for selected snapshot* from incoming timecode in V22, with an offset for a range) and crossfade times per controller type so fader moves glide instead of jump.

## Snapshot groups

Snapshots in a group (red = relative update, blue = non-relative) update together: change a fader in one, the same change goes to the others. Useful for a band's song set where the drum balance should stay consistent.

## Setlists (V22)

Setlists filter and reorder the snapshot list without duplicating anything: the snapshots stay in **ALL SNAPSHOTS** and a setlist just fires them in its own order. Press the **setlist** button for the Setlists panel (New, Duplicate, Rename, Delete, Move); choose one from the dropdown, **Add** snapshots from the full list, **Remove** to take them out of that setlist only. Updating a snapshot from any setlist updates the one original. The Session Information panel shows which setlist is active. Not available in Theatre software.

![Setlists (V22)](/figures/v22-release-notes-p003-1.png)

## Snapshots can trigger other things

MIDI program changes and MIDI lists, GPO relays, macros (Macro Editor > Snapshots tab), external OSC devices, and from V22 LiveTrax markers. See [Macros](/how-to/25-macros).

Manual: [Reference 2.4 Snapshots Menu](/reference/2-4-snapshots-menu), [1.2.5 Channel Safes](/reference/1-2-channel-input-common-elements), [V22 release notes](/docs/v22-release-notes).
