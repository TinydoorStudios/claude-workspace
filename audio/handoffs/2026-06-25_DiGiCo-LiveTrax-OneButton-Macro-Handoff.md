# DiGiCo Q225 → LiveTrax One-Button Macro — Handoff

*2026-06-25 · Memorial Hall / Jazz At The Memo · author: Brian + Cowork*

## TL;DR

Goal: one button on the Q225 that both starts LiveTrax 3 recording and pulls fresh
channel names into LiveTrax, from a single press. Two separate problems, tracked
separately:

1. **Pulling channel names** has no native macro support — only triggerable from
   inside LiveTrax itself ("Create session from console" / "Request ALL channel
   names"). We reverse-engineered the OSC exchange byte-for-byte (below). The
   console-side self-send to replicate it is blocked or broken — confirmed twice,
   zero packets transmit. **Current plan: relay it through Bitfocus Companion**,
   which is a real external device and sidesteps whatever is blocking the
   self-send.
2. **Starting LiveTrax recording** turned out to be unbuilt, not just hard.
   Found the real fix: the Macro Editor has a dedicated **LiveTrax** command
   category (Play / Stop / Rewind / Forward / Return to Start / **Record Arm** /
   Add Marker / Locate Marker / Send Snapshot Markers) — native, no OSC
   guesswork. Mid-build now, macro fires but does nothing yet. Debugging.

Resume at **Next Steps** below.

---

## Network map

| Device | IP | Notes |
|---|---|---|
| Q225 console | 192.168.200.224 | hostname Q225-272459, subnet /16 |
| LiveTrax (Mac) | 192.168.200.166 | listens on UDP 3819 for `/strip/name/N` responses |
| iPad (DiGiCo remote) | 192.168.200.202 | dealer/iPad OSC command set |
| Bitfocus Companion | 192.168.200.54 | always-on; chosen as the relay |

**Console External Control setup** (Setup tab → External Control → External
Devices table, columns Type / Name / IP / Send / Rcv / Enabled):

| Type | Name | IP | Send | Rcv |
|---|---|---|---|---|
| LTrax | mac | 192.168.200.166 | 3819 | 1024 |
| DiGiCo | ipad | 192.168.200.202 | 9001 | 8001 |

Column semantics (cross-validated against the capture): **Send** = port the
console transmits *to* that device. **Rcv** = port the console listens on *for*
that device. So the console listens on **1024** for LiveTrax requests and
answers on **3819**.

---

## Protocol — decoded from capture

Reference capture: `digico-livetrax-macro/reference-capture_request-names-exchange.pcapng`
(the canonical one — captured during a real "Create session from console" press
in LiveTrax). Parser: `digico-livetrax-macro/osc_parser.py` (struct-based,
big-endian, 4-byte-aligned OSC decode — reusable for any future capture).

**Request** (LiveTrax → console, UDP 192.168.200.224:1024):
```
/request_names   ,i   [1]
```

**Response** (console → LiveTrax, UDP 192.168.200.166:3819) — 72 individual
packets, one per channel:
```
/strip/name/N   ,si   [<channel name>, <flag>]
```
`flag = 1` on every channel except the **last**, which carries `flag = 2` as an
end-of-list marker.

**Unrelated heartbeat** also seen on the wire: `/strip/list` (no args), port
8000, on its own interval — not part of the request/response pair, ignore it.

This is the exact message we need fired at the console to make LiveTrax repopulate
channel names. The console-side response routing (back to 192.168.200.166:3819)
appears to be hardcoded to whatever's registered as the **LTrax**-type device,
not a reply-to-sender — meaning the response always lands at LiveTrax regardless
of where the trigger originates, *if* the trigger arrives on port 1024. That's
the working assumption behind the Companion-relay plan below.

---

## Ruled out

**Console self-send via macro.** Added a new External Device (type MacroOSC,
pointed at the console's own IP, 192.168.200.224:1024), built a macro with an
Integer-OSC row sending `/request_names` to it, fired the macro. Zero packets
transmitted to port 1024 — confirmed in Wireshark. Retried with String-OSC
instead of Integer-OSC: same result, nothing transmits. Both tests showed only
the console's automatic macro-state telemetry (`/Macros/Recall_Macro/N`,
`/Macros/Buttons/state`, sent to the registered LTrax device on *any* macro
fire — built-in behavior, unrelated to what we configured). Root cause not
isolated — could be a self-IP loopback block, could be something specific to
how the "fire macro" test button behaves. **Untested diagnostic, still on the
table if we ever care:** point that same macro row at a real non-self IP (e.g.
the existing ipad device, 192.168.200.202) to see if the self-IP is specifically
what's blocked.

**Companion's DiGiCo_OSC module.** Already configured and working (target
192.168.200.224:8001, receive 8002, dealer/iPad command set, "Poll Macros every
10 Seconds" on). Confirmed its full action list is exhaustive — Fire next
snapshot, Fire previous snapshot, Fire snapshot, Macro, Mute Aux, Mute channel,
Mute Control Group, Mute Group Output, Phantom channel, Set fader of channel,
Solo channel. No generic/raw OSC send action. Can't use it to send
`/request_names` directly. (Its "Macro" action — recall a macro by number — may
still be useful for the record-start side, once that macro is named/numbered.)

---

## Current plan

**Side A — channel names (Companion relay):**
Add a **separate, generic OSC connection** in Companion (not DiGiCo_OSC — the
plain "OSC" module type). Target it at 192.168.200.224:1024. Use its raw
send-message action to fire `/request_names` with one integer argument, `1` —
byte-for-byte what LiveTrax itself sends. Since Companion is a genuinely
external device, this should sidestep whatever's blocking the console's
self-send.

**Side B — record start (native LiveTrax macro category):**
Macro Editor → command type **LiveTrax** (separate list from MacroOSC) →
commands available: Play, Stop, Rewind, Forward, Return to Start, **Record
Arm**, Add Marker, Locate Marker, Send Snapshot Markers. This is the real,
documented, non-OSC path DiGiCo provides for LiveTrax transport control.

**Merge:** one Companion button, two actions — generic OSC send (names) +
whatever fires the console's record-start macro (DiGiCo_OSC's "Macro" action,
once that macro is confirmed working, or some other route if Record Arm alone
turns out not to be enough — see below).

---

## Next steps (resume here)

1. **Debug the in-progress record macro.** Brian built a macro named
   `rec_enable_toggle`, assigned to external trigger "OSC 99 on," and was
   inserting the **Record Arm** LiveTrax command into its row. Fired it — no
   effect. Still need answers to:
   - Does the command table actually show the Record Arm command now, or is
     the old placeholder row (`/rec_enable_toggle`, type `i`, value `1`) still
     sitting there unreplaced?
   - Is LiveTrax open and showing connected during the test?
   - Test method: the "fire macro" button inside the editor, or the actual
     assigned trigger (OSC 99 on)?
   - "Doesn't do anything" — totally inert, or something happens in LiveTrax
     just not the expected thing?
2. **Confirm whether Record Arm alone starts recording**, or whether it only
   arms and needs a paired **Play** row in the same macro (Pro Tools-style
   arm-then-play). Likely the real reason "nothing happens" even once Record
   Arm is correctly inserted.
3. Once Side B macro is confirmed working stand-alone on the console: note its
   macro number/name (needed for Companion's DiGiCo_OSC "Macro" action).
4. Build Side A: new generic OSC connection in Companion, target
   192.168.200.224:1024, send-message action for `/request_names` (int, 1).
   Test alone first — fire it, capture in Wireshark, confirm the 72-packet
   `/strip/name/N` burst appears and LiveTrax channel names actually update.
5. Merge into one Companion button (two actions). Test end to end with a real
   show file open in LiveTrax.

---

## Files

- `digico-livetrax-macro/reference-capture_request-names-exchange.pcapng` —
  canonical capture of the real request/response exchange.
- `digico-livetrax-macro/osc_parser.py` — the decoder used to read it (and any
  future capture).

## Open items

- Self-send-to-own-IP root cause never isolated (loopback block vs. macro-fire
  quirk) — not blocking anymore given the Companion-relay pivot, but worth
  knowing if a future macro needs the console to message itself.
- Companion's generic OSC connection needs to be added from scratch — confirm
  exact action name/fields once in the UI (likely "Send message" with Path +
  Arguments, but not yet seen on screen for the generic module specifically).
