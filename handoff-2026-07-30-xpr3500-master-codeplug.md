# Context Handoff — 2026-07-30
**Session topic:** XPR 3500 master codeplug build in MOTOTRBO CPS 2.0, driven over AnyDesk on the Surface machine
**Working file:** `XPR3500 MASTER 2026-07-29.xctb` on the Surface Desktop (saved from the `867TTF2205` archive)

---

## What We Did

Built out the master codeplug by hand. The 6550 archive never made it to the Surface Desktop, so the copy/paste-between-CPS-instances shortcut stayed unavailable and everything was typed in against the values already captured in `KNOWLEDGE/xpr3500-programming-log.md`. Finished and verified the AMERICAN FIREWRK zone (10 analog) and the Rozzi zone (16 analog), then added all 19 contacts. The Event One FX zone is started — the zone exists and Channel1 is fully configured, but the three copies aren't made yet and that work is **unsaved**.

---

## Current State

- **Done, verified, and saved:**
  - **AMERICAN FIREWRK** — 10 analog channels, all simplex, DPL **225** RX and TX, admit Channel Free. Read back every column, validation 0, warnings 0, saved, then re-opened from disk and re-read to confirm it persisted.
  - **Rozzi** — 16 analog channels, all simplex, DPL **023** RX and TX, admit Channel Free. Same full verification pass, same reopen-from-disk check.
  - **19 contacts** — GROUP 01–16 (digital group calls 6100, 6200 … 7600), Portable (digital private 1001), Base (digital private 3001), EVENT ONE FX (digital group 10010). Table read back row by row, validation 0, saved.
- **In progress — NOT SAVED:**
  - Zone **Event One FX** created, and **Channel1** fully configured: digital, RX = TX **464.500000**, Color Code **4**, Repeater/Time Slot 1, Contact Name **EVENT ONE FX**, Group List None, Admit Criteria **Always**, power High, TOT 60, rekey 0, privacy off, scan None.
  - Session stopped with the ⋯ menu open on the Zone Items toolbar, one step short of `Add Copies` → 3.
- **Up next:**
  1. `Add Copies` ×3 off Channel1, then set name + both frequencies on each — **Channel2 464.550000**, **Channel3 469.500000**, **Channel4 469.550000**. The copies carry color code, contact, admit and everything else, so it's three fields per channel.
  2. Delete **AFX 1i–4i** from Zone1 (positions 12–15) now that the full AMERICAN FIREWRK zone exists.
  3. Rename **Zone1 → 3CDC**.
  4. Save, verify all four zones, re-open from disk and re-read.

---

## Key Decisions (Locked)

- **Build by hand, not by copy/paste.** The 6550 archive `376TVB1928.ctb2` is still on the Broadcast machine, not the Surface. Everything gets typed from the captured values in the programming log.
- **AFX 3i = DPL 225** everywhere. The `023` in the old Zone1 was the typo.
- **Rozzi 12 built as found** — 467.875000 / DPL 023, a duplicate of Rozzi 11. Preserve-the-source call. Still reads like a typo in the 6550 and is worth checking against Rozzi's own frequency list some day.
- **The Event One FX digital contact is named `EVENT ONE FX`, not `Call1`.** This overturns decision 3 from 2026-07-29 — **CPS makes `Call1` impossible**, see Watch-Outs. The alias is local to the codeplug; Call ID 10010 is what has to match on the air, so nothing is lost operationally.
- **Event One FX channels keep the source names** `Channel1`–`Channel4` — that's what their crew calls them over the air.
- **Event One FX admit criteria = `Always`**, matching their source codeplug rather than the politer `Channel Free` used on Brian's own analog zones.

---

## Open Items

- The Event One FX zone is unsaved. First move in the next session is to confirm what's actually in the file before adding anything.
- Rozzi 11 vs Rozzi 12 duplicate frequency — built as found, never confirmed against Rozzi's list.
- Radio ID roster for the fleet — every radio needs a unique one. Use **Clone**, not Clone Express, on new radios so the ID gets assigned during the push.
- Two other fleet radios sit on the Surface Desktop and will need the master pushed to them: **`867TTKA340`** (6 analog venue channels, last programmed 2025-08-23) and **`867TTF4358`** (only 4 channels, last programmed **2017** — nine years stale, missing the Memo channels). Both are model `H02RDH9VA1AN`, same as the master's base radio, so Clone works.
- Nothing has been written to a radio yet. Verify one radio against one of Event One FX's on each channel before cloning out to the fleet.

---

## Files Updated This Session

| File | Description |
|------|-------------|
| `KNOWLEDGE/xpr3500-programming-log.md` | The job file — as-built tables for AMERICAN FIREWRK and Rozzi, verification records, build-progress table, and the CPS operating notes below |
| `about-me/memory.md` | Two session notes covering the manual build and the Rozzi `Add Copies` method |

---

## Corrections / Watch-Outs

CPS-over-AnyDesk mechanics that cost time this session and are now written into the programming log:

- **`Ctrl+A` before typing in any field.** Triple-click does *not* select the contents — it leaves the caret in place, so the text gets inserted and you get a concatenated value that silently reverts with a `Value is out of Range` warning.
- **Edit channels through the pencil → form view, not the grid.** The `RX/TX` section tab puts fields at repeatable coordinates.
- **Reset the zone grid's horizontal scroll to the far left before clicking a row selector.** If it's still scrolled right from a verification read, the row never selects and the following clicks land on arbitrary cells — checkboxes included. Cost one wasted pass; caught on read-back, nothing altered.
- **Commit a field with a neutral click before clicking a breadcrumb.** A breadcrumb click while a spin-edit still has focus gets swallowed, and the next actions operate on the wrong record. This is what put 6400 into GROUP 03 — caught and corrected to 6300.
- **One contact per batch.** Two-contacts-per-batch failed for the reason above.
- **A zone caps at 16 channels** — the ⊕ Add button greys out there.
- **`Add Copies` carries everything** — frequency, squelch types, DPL codes, admit, power, TOT, unmute, turn-off code. Copies arrive named `ChannelNN`, so each costs only name + RX freq + TX freq.
- **CPS refuses duplicate contact names.** Naming a second contact `Call1` red-flags the field and throws two validation errors, `\Contacts:Call1\Contact` / code `700101000` / "Invalid item needs to be removed" — on *both* the new and the original. And a contact container accepts only **one** Digital entry (the second ⊕ Digital greys out), so nesting the 10010 call under the existing `Call1` isn't possible either. Hence the rename.
- **The Mac locked mid-session** while the archive had unsaved changes. Save after each zone.

---

## Resume Prompt

> Picking up from a previous session on the XPR 3500 master codeplug, working in MOTOTRBO CPS 2.0 on the Surface machine over AnyDesk. Working file is `XPR3500 MASTER 2026-07-29.xctb` on that Desktop. Read `KNOWLEDGE/xpr3500-programming-log.md` first — it has the as-built tables, the CPS operating notes, and the build-progress state.
>
> Done and saved: the AMERICAN FIREWRK zone (10 analog, DPL 225), the Rozzi zone (16 analog, DPL 023), and all 19 contacts. Each was verified column by column with zero validation errors and re-read from disk after saving.
>
> In progress and **unsaved**: the Event One FX zone exists with Channel1 built — digital, RX = TX 464.500000, Color Code 4, slot 1, contact EVENT ONE FX, group list None, admit Always. Check what's actually in the saved file before adding anything.
>
> Next: `Add Copies` ×3 off Channel1 and set name plus both frequencies on each — Channel2 464.550000, Channel3 469.500000, Channel4 469.550000. Then delete AFX 1i–4i from Zone1 (positions 12–15) and rename Zone1 to 3CDC. Then save, verify, and re-open from disk to confirm.
>
> Two things to carry: the Event One FX contact is named `EVENT ONE FX`, not `Call1` — CPS rejects duplicate contact names outright and allows only one digital entry per contact, so the 2026-07-29 decision to preserve the `Call1` name is dead. And use `Ctrl+A` before typing in any CPS field; triple-click doesn't select and produces a silently-reverted concatenated value.
