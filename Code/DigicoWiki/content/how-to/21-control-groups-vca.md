# Control groups (VCA-style masters)

A Control Group (CG) moves the faders and mutes of its members. It carries no audio, unlike a Group bus. The Q225 has 12; the count is set in Session Structure. CGs live on layer 2 by default.

![Control Groups panel](/figures/q2-control-groups.png)
*Control Groups panel — Quantum 2 offline software, V22.*

## Make one

Either:

1. Press **LCD Function** on the CG bank, then **JOIN CG**. Press the CG's select button, then the select button of every channel to include, then deselect JOIN CG.

or:

2. On the CG's on-screen strip press **JOIN/LEAVE**, press the members' select buttons, release JOIN/LEAVE.

![Join CG](/figures/ref-p139-2.png)
*Manual figure: Join CG — LCD Function > Join CG, select the control group, then the member channels — SD Quantum Software Reference, Issue H, p.139.*

Members are listed at the top of the CG strip. **Clear** empties it. Name it with the usual name box. A channel shows its CG memberships above its GANG/SAFE buttons (only the first two or three fit).

## Fader modes

The button under **clear** cycles three modes: **moving fader** (member faders physically follow), **VCA style** (member levels change but faders stay put), **mute only**. Changes are relative in dB: +2 dB on the CG is +2 dB on every member regardless of where they sit.

## Mutes

The CG mute (and the **all mute** button on the strip) mutes every member; the member's CG MUTE indicator goes blue. Multiple CGs are in series: all must be unmuted for the channel to pass. A channel's own mute button overrides its CG mutes without leaving the group. **auto-mute** mutes a channel when it leaves the group and unmutes it when it joins.

## Spill and aux sends

**Spill** on the CG strip (or a *Spill Control Group* macro) puts the members on the surface. The **aux sends** button lets the CG fader trim the aux sends of its members when Aux to Faders is active; in V22 group faders can be included too (Options > Solo > *Aux to Faders includes Group*).

**safe** at the bottom of the CG strip protects its membership and settings from snapshots.

Master screen > **Control Groups** shows all of them side by side with spill, join/leave, clear and all-mute.

Manual: [Reference 2.9 Control Groups](/reference/2-9-control-groups), [Getting Started 1.13](/console/1-13-control-groups).
