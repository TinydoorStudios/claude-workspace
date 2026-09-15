# Memorial Hall: how the Q225 is set up

The Q225 is the house console at Memorial Hall (Jazz At The Memo and everything else in the room). 556 seats, hardwood stage 37'4" × 22'3", built 1908, renovated 2016. Working RT60 is about 1.6 s with an audience. Piano storage is stage right.

## Session workflow

Shows start from the Memo template session (`brian memo june 2026.ses`, current since 2026-07-01). Never edit the template; each show gets its own copy, built from the show packet, in that show's folder. Mustard processing is **off** on every channel by default.

## Fader layout that doesn't move

| Faders | What lives there |
|---|---|
| 41 / 42 / 43 / 44 | House wireless 1 / 2 / 3 / 4 |

The rest follows the show packet.

## VCA layout

| VCA | Contents |
|---|---|
| Drums | all drum channels |
| Instruments | guitars, keys, bass, horns, strings |
| Vocals | all vocal channels |
| FX | effects returns |

## Crowd / ambient mic rig

Patched for every Memo show (the channel numbers vary by packet, the rig doesn't):

| Pair | Where | What it's for |
|---|---|---|
| Line Audio OM1 (omni pair) | flown 18' above the stage, 12' apart | ambient / FOH colour |
| Deity S2 (short shotgun pair) | under the main-floor PA, aimed into the audience | audience |
| Line Audio CM4 (ORTF cardioid pair) | balcony rail, facing back into the room, 34' behind the Deity pair | room |

These feed the recording and a touch of the house mix. Always high-pass them and treat the room's build-up (below) before adding any.

## The room's problem frequencies

Standing waves at 63 Hz, 125 Hz, 200 Hz and 250–315 Hz, and a mud build-up across 200–400 Hz. Every show packet already treats these; if something sounds boomy mid-show, that's where to look first. Classical shows in this room are mixed minimally: spots blend, nothing aggressive.

## Recording

Every show is multitracked. The record chain (Companion button → REAPER on the Memo machine) has three record buttons that are **not** equivalent — two bypass the relay. Read the [Memo REAPER record chain SOP](https://kb.tinydoorstudios.com/sop-memo-reaper-record-chain) before touching it.

## Network note

Dante at Memo rides VLAN 200 on the backstage SG350 switch. IGMP snooping on that VLAN starved the Dante Via Mac of PTP once (two clock leaders, green subscriptions with no audio); snooping is disabled on VLAN 200 for that reason. Don't re-enable it. See [Dante and the Cisco switches](https://kb.tinydoorstudios.com/dante-cisco-switch-config).

## When to stop and call Brian

Loading a different session, recalling snapshots you didn't build, re-patching, changing clocking, or anything on the record chain during a show.

Related: [Console: DiGiCo Quantum 225](https://kb.tinydoorstudios.com/console-digico-q225) · [Memorial Hall venue page](https://kb.tinydoorstudios.com/venue-memorial-hall) · [Reverb reference (Memo)](https://kb.tinydoorstudios.com/reverb-reference-memo)
