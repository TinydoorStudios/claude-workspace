# Fountain Square: how the Q225 is set up

FOH is the Quantum 225. Monitors are on a Midas M32 (its own desk, its own engineer); the Q225 does not mix wedges at FSQ. PA is L-Acoustics: four A15 per side, eight KS21 subs in a delayed arch, eight X12 wedges on stage. The SPL limit at the square is **95 dBA, Slow** — both qualifiers, always.

## Session workflow

Every show starts from the FSQ template session; it is never edited directly. The show file is built from the show packet (channel names, EQ, patch) and loaded at the top of the day. If you need to change something on a show file, change it on the show file, not the template. Mustard processing is **off** on every channel by default and only gets switched on deliberately.

Save before you leave. See [Save a session](/how-to/03-save-a-session).

## Fader layout that doesn't move

| Faders | What lives there |
|---|---|
| 9 | Overheads, stereo channel |
| 10 | Snare PL8 return (the snare trigger return, not the top mic) |
| 33 / 34 / 35 / 36 | House wireless 1 / 2 / 3 / 4 |
| 47–56 | Spares |
| 57 | Click — Tempo |
| 58 | FOH Playback |

Drums are the first block of faders; the band's inputs follow the show packet. Toms are gated in the channel's native gate block (not Mustard) with per-drum sidechain settings baked into the template.

## Wireless

Wireless 1–4 always land on 33–36. If a band's input list names a specific unit ("Wireless 2", "W58 2"), that receiver is *multed*: the band's channel keeps its own fader **and** the wireless fader stays listed, same source port on both. Analog gain is shared between the two channels on a Q225, so ride the digital trim on the mult, never the gain. A bare "W58" with no unit number on a list means stop and ask — never assign a pack by guessing.

## EQ philosophy outdoors

Cuts at FSQ go one step deeper than indoors: −6 to −9 dB typical on problem frequencies, up to −10 on low-mid mud. Clarity first. The show packet's EQ pages already reflect this; don't dial it back to indoor numbers because it looks aggressive on the screen.

## When to stop and call Brian

Loading a different session, recalling snapshots you didn't build, re-patching stage inputs, or changing clocking during a show. Anything with a packet page that disagrees with what you see on the desk.

Related: [Console: DiGiCo Quantum 225](https://kb.tinydoorstudios.com/console-digico-q225) · [Fountain Square venue page](https://kb.tinydoorstudios.com/venue-fountain-square) · [M32 failover SOP](https://kb.tinydoorstudios.com/sop-fsq-m32-failover)
