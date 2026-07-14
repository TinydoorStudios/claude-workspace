# DiGiCo Q225 → LiveTrax — One-Button Record Chain (Phase 2)

*2026-06-25 · Memorial Hall / Jazz At The Memo · author: Brian + Nyquist*

## Goal

LiveTrax now lives on the **.54 PC** alongside Companion. Build two Companion
buttons:

- **RECORD** — one press does, in order: (1) pull fresh channel names into
  LiveTrax, (2) arm all tracks, (3) wait 5 seconds, (4) start recording.
- **STOP** — one press stops the LiveTrax recording.

This doc is the build-and-test playbook. Load it once LiveTrax is installed on
.54 and the console is reachable. Work the steps in order — each has a clear
pass/fail check before moving on.

---

## What we proved on 2026-06-25 (don't re-litigate)

These are hard facts from a full session of live testing against the console
and a real LiveTrax session. They define why the build looks the way it does.

1. **Pull-names message is exact and known.** The "Create session from console"
   button in LiveTrax sends one OSC packet to the console:
   ```
   /request_names  ,i  1
   hex: 2f726571756573745f6e616d657300002c69000000000001
   → UDP to console 192.168.200.224 : port 1024
   ```
   The console answers with **72** packets `/strip/name/N ,si [name, flag]` —
   `flag=1` on every channel, `flag=2` on the last (end-of-list marker) — sent
   to the registered LTrax device on **port 3819**.

2. **The console only honors `/request_names` from the IP registered as its
   LTrax device.** A send from the registered machine works; a send from any
   other IP is silently ignored. (Companion at .54 firing straight at the
   console failed for exactly this reason while the Mac at .166 succeeded.)

3. **The console delivers names to the registered device's IP:3819 regardless
   of who triggered** — it is *not* reply-to-sender. So names always land at
   whatever is registered, as long as the trigger arrives from that same IP.

4. **Source port does not matter; source IP does.** Ephemeral ports all worked.

5. **macOS quirk (may or may not apply on Windows):** a *long-lived* in-process
   UDP socket would NOT trigger the console — only a freshly-spawned process per
   send did. On the Mac we worked around it with a tiny relay that spawns a
   fresh Python process per poke. **Whether this quirk exists on the Windows
   .54 box is unknown and is the first thing to test below.** If it doesn't,
   Companion can talk straight to the console with no relay.

6. **`pull-names` ≠ "create session."** It only repopulates names into a
   session that is already open. So a template session must already be loaded
   in LiveTrax (72 tracks). There is no remote "make new session" command.

7. **The console rate-limits `/request_names`** — two requests close together,
   it answers the first and ignores the second. One press = one pull. Fine for
   human-paced button presses; just don't double-tap.

Reference capture + parser + relay script live in
`digico-livetrax-macro/` (same folder as the original Phase 1 handoff).

---

## Target network map (Phase 2)

| Device | IP | Role |
|---|---|---|
| Q225 console | 192.168.200.224 | listens :1024 for requests, sends names :3819, transport via macros |
| **.54 PC** | 192.168.200.54 | runs **both** Companion **and** LiveTrax now |
| (Mac .166) | — | retired, out of the picture |

**Console External Control change (do this first):** in Setup → External
Control → External Devices, the **LTrax** device must be re-pointed from the
old Mac (.166) to the **.54 PC**:

| Type | Name | IP | Send | Rcv |
|---|---|---|---|---|
| LTrax | pc | **192.168.200.54** | 3819 | 1024 |

(Send = port console transmits names to the device on = 3819. Rcv = port
console listens on for requests = 1024.) Until this is changed, the console
will still try to send names to the dead Mac and ignore requests from .54.

---

## Part 1 — Names pull from .54

Now that .54 is the registered LTrax device, test the simple path first.

### 1A. Try Companion → console directly (no relay)

- Companion connection (the existing **LiveTrax / Generic: OSC**): set Target
  Host `192.168.200.224`, Target Port `1024`, UDP.
- Button action: **Send integer**, OSC Path `/request_names`, Value `1`.
- Open LiveTrax with the 72-track template loaded. Junk a few track names so a
  successful pull is visible.
- Press the button **once**. Wait. Did the junk names flip to the real console
  names?

**PASS** → names path is done, no relay needed. Skip 1B.
**FAIL** → the long-lived-socket quirk (fact 5) bites on Windows too. Go to 1B.

### 1B. Relay fallback on .54 (only if 1A failed)

Run the relay on the .54 PC. It listens on UDP 9000 and spawns a fresh process
per poke to fire `/request_names` — sidestepping the long-lived-socket quirk.

- Copy `digico-livetrax-macro/livetrax_relay.py` to the .54 PC. It's pure
  Python 3, no dependencies — runs on Windows as-is. Install Python 3 if needed.
- Run it: `python livetrax_relay.py` (or set it as a Startup task / NSSM service
  so it auto-starts — Windows equivalent of the launchd service we'd have used
  on the Mac).
- Companion connection: Target Host `127.0.0.1` (localhost — Companion and the
  relay are both on .54 now), Target Port `9000`, UDP.
- Button action: **Send integer**, OSC Path `/pull`, Value `1` (any payload
  triggers the relay).
- Junk names, press once, confirm flip.

Either way, the end result is: **one Companion action that repopulates names.**
Call it the "pull names" action — it's step 1 of the RECORD button below.

---

## Part 2 — Record / Arm / Stop via console LiveTrax macros

Transport control runs through the **console's** native LiveTrax macro
commands, fired from Companion. The console talks to LiveTrax over the LTrax
link (the same link that now points at .54), so this is the documented,
non-guesswork path.

### 2A. Build the console macros

In the Q225 Macro Editor, the command category **LiveTrax** offers: Play, Stop,
Rewind, Forward, Return to Start, **Record Arm**, Add Marker, Locate Marker,
Send Snapshot Markers. Build three macros and note each one's **macro number**:

| Macro | Contents | Purpose |
|---|---|---|
| `LT_ARM` | LiveTrax **Record Arm** | arm tracks for recording |
| `LT_REC` | LiveTrax **Play** | roll the armed transport = record |
| `LT_STOP` | LiveTrax **Stop** | stop recording |

> **Test each macro standalone on the console first** (fire it from the Macro
> Editor with LiveTrax open) before wiring Companion. This is where Phase 1
> stalled — a macro that "fires but does nothing" usually means the command row
> didn't actually get the LiveTrax command inserted, or LiveTrax wasn't showing
> connected. Confirm each does its thing in LiveTrax before continuing.

**Two things to determine during this test — they decide the button layout:**

- **Does "Record Arm" arm all 72 tracks, or just toggle global record-ready?**
  If LiveTrax already record-enables all inputs by default, the arm step may be
  redundant and `LT_ARM` can be dropped. Watch the track arm states when you
  fire it.
- **Does "Play" alone start recording once armed, or is recording a separate
  engage?** Working theory (Pro-Tools model): Record Arm + Play = recording.
  If Play only plays back, look for whether Record Arm itself rolls the
  recorder, and adjust. Confirm by watching LiveTrax actually capture audio.

### 2B. Fire the macros from Companion

Companion's **DiGiCo_OSC** connection (already configured, target
192.168.200.224) has a **"Macro"** action that recalls a console macro by
number. Use it to fire `LT_ARM`, `LT_REC`, `LT_STOP` by their numbers from 2A.

(If macro-by-number proves unreliable, the alternative is a generic-OSC send of
the console's macro-recall OSC path — but try the native DiGiCo_OSC "Macro"
action first; it's the supported route.)

---

## Part 3 — Assemble the buttons

### RECORD button (one press = full chain)

Press actions, in order:

1. **Pull names** — the action from Part 1 (direct `/request_names` int 1, or
   `/pull` to the relay).
2. **Arm** — DiGiCo_OSC "Macro" → `LT_ARM` number. *(Drop this step if 2A showed
   Record Arm is redundant.)*
3. **Wait 5000 ms** — Companion's built-in delay. In the action list add **wait
   / time delay = 5000ms** between the arm and the record action. (Companion
   runs press actions top-to-bottom; the delay holds before the next one.)
4. **Record** — DiGiCo_OSC "Macro" → `LT_REC` number.

### STOP button

1. **Stop** — DiGiCo_OSC "Macro" → `LT_STOP` number.

Give the buttons clear labels/colors (RECORD red, STOP grey). Optionally keep a
standalone **Name** button (just step 1) for manually re-pulling names without
recording — that's the button already built and working.

---

## Test plan (work top to bottom, stop at any FAIL)

1. Re-point console LTrax device to .54. ✅ when console shows it connected.
2. Part 1A direct names pull. ✅ junk names flip. ❌ → do 1B relay.
3. Each console macro standalone (`LT_ARM`, `LT_REC`, `LT_STOP`) with LiveTrax
   open. ✅ each visibly does its job. Resolve the two 2A questions here.
4. Companion fires each macro individually (DiGiCo_OSC "Macro" by number).
   ✅ same behavior as firing on the console.
5. Build the RECORD button, press once: names pull → arm → 5s → record rolls,
   LiveTrax capturing audio. ✅
6. Press STOP: recording stops cleanly. ✅
7. Full dress rehearsal: blank/junk names, fresh template, one RECORD press,
   let it run, STOP. Confirm the take has correct track names and audio.

---

## Open questions / risks (know these going in)

- **Long-lived-socket quirk on Windows (fact 5):** unknown until 1A is tested.
  If it bites, the relay (1B) is the answer and must auto-start on the .54 PC.
- **Record Arm semantics (2A):** arm-all vs global-ready, and Play-rolls-record
  vs needs-separate-engage. Both resolved by the standalone macro test in 2A —
  don't build the button until they're settled.
- **Template session must be open in LiveTrax** before any of this works
  (fact 6). If LiveTrax has no session loaded, names fall on the floor and there's
  nothing to record into. Consider a saved 72-track template that's loaded at
  show start.
- **Don't double-tap** the names pull (fact 7 rate-limit).
- **5-second wait is a starting value** — if names/arm need longer to settle in
  practice, bump it.

---

## Files (in `digico-livetrax-macro/`)

- `reference-capture_request-names-exchange.pcapng` — canonical capture of the
  real request/response exchange (re-captured + verified 2026-06-25).
- `osc_parser.py` — struct-based OSC decoder for reading any future capture.
- `livetrax_relay.py` — the fresh-process-per-poke relay (the 1B fallback).
  Listens UDP 9000, fires `/request_names` to the console. Pure Python 3,
  Windows-compatible.
- `send_request_names.py` — standalone one-shot sender (fires the exact
  `/request_names` bytes once; useful for manual testing on whatever box is the
  registered LTrax device).

---

## Bottom line

Yes, this is buildable, and the hard unknowns from Phase 1 are now answered.
The names pull is proven; the record path is a documented native macro chain;
Companion can fire all of it. The only live unknowns left are Windows socket
behavior (Part 1A vs 1B) and the exact Record Arm / Play semantics (Part 2A) —
both have explicit go/no-go tests above. Work the plan in order and the
one-button record + stop is a short build from here.

— Nyquist
