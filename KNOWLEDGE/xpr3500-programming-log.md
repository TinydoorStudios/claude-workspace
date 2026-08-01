# XPR 3500 Fleet — Programming Log

*Running working file for Brian's XPR 3500 fleet build. How-to and field reference live in [motorola-cps-reference.md](motorola-cps-reference.md); this file is the job: what's going on the radios, where it came from, and what's still open. Appended as we go.*

**Fleet:** Motorola XPR 3500, UHF business band · **System:** conventional, direct/simplex, no repeater · **Software:** MOTOTRBO CPS 2.0 on the remote PC, reached over AnyDesk.

---

## Zone plan

One zone per client, kept separate. See the master codeplug build plan further down for the consolidated target.

| Zone | Contents | Status |
|---|---|---|
| AMERICAN FIREWRK | 10 analog, DPL 225 | built + verified 2026-07-30 |
| 3CDC | 11 analog venue channels (renamed from Zone1, AFX 1i–4i removed) | built + verified 2026-07-30 |
| Rozzi | 16 analog, DPL 023 | built + verified 2026-07-30 |
| Event One FX | 4 digital, CC 4 / TG 10010 | built + verified 2026-07-30 |

---

## Channel set 1 — Event One FX (guest system)

Not Brian's license. These are another company's frequencies, provided by them so his radios can work alongside their fleet. Captured 2026-07-29 from their codeplug `Event One FX CP200 4 Channel Digital.xctb`, open in CPS on the remote PC.

**Source radio:** CP200d — model `H01QDC9JA2AN`, Tanapa `PMUE4147BA`, region NA, serial `752TVH1767`, UHF 403–470 MHz, Firmware Type Digital, firmware `R01.01.30.0000`, codeplug version `11.00.46`, last programmed 2026-02-03.

### Channels — all digital, all simplex (TX = RX)

| # | Name | RX = TX (MHz) | Color Code | Slot | Contact | RX Group List | Admit | Power | TOT |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Channel1 | 464.500000 | 4 | 1 | Call1 | None | Always | High | 60 s |
| 2 | Channel2 | 464.550000 | 4 | 1 | Call1 | None | Always | High | 60 s |
| 3 | Channel3 | 469.500000 | 4 | 1 | Call1 | None | Always | High | 60 s |
| 4 | Channel4 | 469.550000 | 4 | 1 | Call1 | None | Always | High | 60 s |

These are the standard UHF itinerant pairs — 464.500/469.500 (red dot) and 464.550/469.550 (blue dot) — run as four simplex channels rather than two repeater pairs.

### Contact

One entry in the whole source codeplug: **`Call1` — Digital Calls, Group Call, Call ID `10010`.**

### The three that must match exactly

Frequency · **Color Code 4** · **Talkgroup 10010**. Miss the color code or the talkgroup and the radio sits silent on a correct frequency with no error and no noise.

### Everything else in the source (for completeness)

Digital RX Group List `List1` exists but is **empty** and no channel references it — reception rides on the contact's auto-included Call ID. Scan/Roam List `None` and Auto Scan No on every channel, so scan is off despite a `List1` existing under Scan Items. Privacy No, ARS Disabled, RAS `None`, Allow Talkaround greyed (correct for TX=RX), Extended Range Direct Mode Disabled, DCDM unchecked, Timing Leader Eligible, RX Only off, TX VOX off, TOT Rekey Delay 0, In Call Criteria Always, RSSI threshold −124 dBm, Private Call Confirmed off, Data Call Confirmed on, Enhanced Channel Access No. Network set stock: Radio IP 192.168.10.1, CAI Network 12, CAI Group Network 225.

### How it gets onto the XPR 3500s

Clone and Clone Express both require the same radio model, so a CP200d archive can't be pushed onto an XPR 3500. Set-level copy/paste between two CPS 2.0 instances would work, but for four channels, building them by hand in the XPR archive is faster and avoids dragging CP200d-specific settings across. Build order: Contact `Call1` (Group Call, 10010) → the four channels → new zone → assign.

Then verify one radio against one of theirs on each channel before cloning out to the fleet.

---

## Channel set 2 — XPR 6550 codeplug `376TVB1928.ctb2` (read 2026-07-29)

Brian's own radio. Three zones, 28 channels, **all analog** — no digital channels anywhere in this codeplug despite a full set of digital contacts sitting unused.

**Source radio:** model `H02RDH9VA7AN`, Tanapa `PMUE3836BN`, region NA, serial `376TVB1928`, UHF **403–512 MHz**, firmware `R02.09.01.0001`, codeplug version `14.00.13`, bootloader `R02.09.00.0000`, last programmed 2023-09-30. Product family: MOTOTRBO 2.0 Subscribers. Feature sets: Digital `Free & Used`; Digital Emergency, Radio Inhibit, Extended Text Messages, Remote Monitor all `Free`.

### Settings common to all 28 channels

Analog · 12.5 kHz · **simplex (TX = RX)** · Squelch Normal · Voice Emphasis De & Pre · Unmute Rule Std Unmute, Mute · RX Signaling System None · Scan/Roam List None · Auto Scan No · ARTS Disabled · Lone Worker No · Allow Talkaround No · Audio Enhancement None · Scrambling off · RX Only off · **Power High** · **TOT 60 s** (rekey delay 0) · **Admit Criteria Channel Free** · TPL Reverse Burst Standard · DPL Turn-Off Code checked · RSSI threshold −124 dBm · VOX off.

Only the frequency and DPL code differ between channels, so the tables below carry just those.

### Zone: AMERICAN FIREWRK — 10 channels, DPL **225** (RX and TX)

| # | Name | RX = TX (MHz) |
|---|---|---|
| 1 | AFX 1i | 462.862500 |
| 2 | AFX 2i | 467.862500 |
| 3 | AFX 3i | 456.800000 |
| 4 | AFX 4i | 464.550000 |
| 5 | AFX 5i | 462.837500 |
| 6 | AFX 6 - Cinci | 464.825000 |
| 7 | AFX 7 - Cinci | 469.825000 |
| 8 | AFX 8 - Cinci | 464.125000 |
| 9 | AFX 9 - Cinci | 469.125000 |
| 10 | AFX 10 - Cinci | 467.850000 |

### Zone: 3CDC — 2 channels

| # | Name | RX = TX (MHz) | DPL (RX & TX) |
|---|---|---|---|
| 1 | FSQ Production | 451.212500 | 116 |
| 2 | WP Production | 451.887500 | 331 |

### Zone: Rozzi — 16 channels, DPL **023** (RX and TX)

| # | Name | RX = TX (MHz) |
|---|---|---|
| 1 | Rozzi 1 | 464.550000 |
| 2 | Rozzi 2 | 456.787000 |
| 3 | Rozzi 3 | 456.812000 |
| 4 | Rozzi 4 | 456.857000 |
| 5 | Rozzi 5 | 456.862000 |
| 6 | Rozzi 6 | 456.887000 |
| 7 | Rozzi 7 | 469.550000 |
| 8 | Rozzi 8 | 469.500000 |
| 9 | Rozzi 9 | 467.925000 |
| 10 | Rozzi 10 | 467.900000 |
| 11 | Rozzi 11 | 467.875000 |
| 12 | Rozzi 12 | 467.875000 |
| 13 | Rozzi 13 | 467.812000 |
| 14 | Rozzi 14 | 467.762000 |
| 15 | Rozzi 15 | 464.825000 |
| 16 | Rozzi 16 | 467.712000 |

### Contacts (20)

| Name | Type | Call ID |
|---|---|---|
| GROUP 01 – GROUP 16 | Digital Group Call | 6100, 6200, 6300, 6400, 6500, 6600, 6700, 6800, 6900, 7000, 7100, 7200, 7300, 7400, 7500, 7600 |
| Portable | Digital Private Call | 1001 |
| Base | Digital Private Call | 3001 |
| Call1 | MDC Group Call | E001 |
| Call1 | Quik-Call II | 138 |

Channel Pool empty. Digital RX Group List `List1` exists but is **empty** (all 16 groups sit in Available). Scan list `List1` has only the placeholder "Selected" as a member, and no channel points at it — scan is off.

### Flags worth a look

- **Rozzi 11 and Rozzi 12 are both 467.875000** with the same DPL 023 — two identical channels. Probably a typo in one of them; worth checking against the source list before it goes into the master.
- Sixteen digital group contacts and a digital RX group list exist with no digital channel using them — leftovers from an earlier build.

### Frequency overlaps between zones — not an issue (Brian, 2026-07-29)

Several frequencies repeat across zones: Rozzi 1 = AFX 4i (464.550), Rozzi 15 = AFX 6 (464.825), and Rozzi 7/8 (469.550 / 469.500) are the same pair as Event One FX Channel 4 / Channel 3 — analog DPL 023 on Brian's side, digital color code 4 on theirs.

**No conflict in practice: the zones are per-client and never in use at the same time.** No need to re-plan frequencies or worry about analog/digital coexistence on the shared ones. Only relevant if that ever changes — analog and digital cannot share a frequency simultaneously, and Channel Free admit would hold off transmit while another group is talking on the same carrier.

---

## Channel set 3 — the target XPR 3500 codeplug `867TTF2205` (read 2026-07-29)

**This is not an empty radio.** It's a live working codeplug with 15 channels already in it, and it's the base the master gets built on.

**Radio:** model `H02RDH9VA1AN`, Tanapa `PMUE3836BK`, region NA, serial `867TTF2205`, UHF **403–512 MHz**, firmware `R02.07.01.0000`, codeplug version **11.00.17**, bootloader `R02.07.00.0000`, last programmed 2025-08-23.

*(Note: the "6550" reads `H02RDH9VA7AN` / Tanapa `PMUE3836BN` — same family, one character apart, but not the same model number, so Clone still won't cross between them. It's also on codeplug 14.00.13 vs 11.00.17 here.)*

### Zone1 — 15 analog channels, all simplex (TX = RX), all 12.5 kHz

| # | Name | RX = TX (MHz) | DPL (RX & TX) | Admit |
|---|---|---|---|---|
| 1 | FSQ-OPS | 451.037500 | 043 | Always |
| 2 | FSQ-PROD | 451.212500 | 116 | Always |
| 3 | FSQ-GARAGE | 451.537500 | 143 | Always |
| 4 | WP-OPS | 451.687500 | 174 | Always |
| 5 | WP-PROD | 451.887500 | 331 | Always |
| 6 | WP-GARAGE | 452.337500 | 465 | Always |
| 7 | OTR-DIST | 452.462500 | 734 | Always |
| 8 | MEM-PROD | 451.212500 | 244 | Always |
| 9 | MEM-FOH | 451.537500 | 125 | Always |
| 10 | ZIEGLER | 451.037500 | 546 | Always |
| 11 | BBB | 451.687500 | 172 | Channel Free |
| 12 | AFX 1i | 462.862500 | 225 | Channel Free |
| 13 | AFX 2i | 467.862500 | 225 | Channel Free |
| 14 | AFX 3i | 456.800000 | **023** | Channel Free |
| 15 | AFX 4i | 464.550000 | 225 | Channel Free |

All: power High, TOT 60 s, rekey delay 0, RSSI −124, squelch Normal, De & Pre, Unmute Rule Std Unmute/Mute, DPL Turn-Off Code checked, no signalling system, scrambling off. **WP-OPS is the only channel with a scan list attached** (`ScanItems/List1`, Auto Scan unchecked).

Note the venue channels reuse five frequencies in pairs on different DPL codes — 451.0375 (FSQ-OPS 043 / ZIEGLER 546), 451.2125 (FSQ-PROD 116 / MEM-PROD 244), 451.5375 (FSQ-GARAGE 143 / MEM-FOH 125), 451.6875 (WP-OPS 174 / BBB 172).

### Contacts (3) — all named `Call1`

| Name | Type | Call ID |
|---|---|---|
| Call1 | MDC Group Call | E001 |
| Call1 | Quik-Call II | 138 |
| Call1 | Digital Group Call | **1** |

### Scan list `ScanItems/List1` — populated and in use

Members: Selected, FSQ-OPS, FSQ-PROD, MEM-PROD, FSQ-GARAGE, WP-OPS, WP-PROD, WP-GARAGE, OTR-DIST.
Not members: MEM-FOH, ZIEGLER, BBB, AFX 1i–4i.
Talkback on, PL Type "Priority and Non-Priority Channel", Channel Marker on, TX Designated Channel Zone None.

Digital RX Group List `List1` exists and is empty. Channel Pool empty.

### What this means for the merge

- **The 6550's "3CDC" zone is redundant.** Its two channels are already here: FSQ Production 451.2125/116 = `FSQ-PROD`, WP Production 451.8875/331 = `WP-PROD`. Nothing new to add from that zone.
- **AFX 1i–4i already exist in Zone1** and would be duplicated by a full AMERICAN FIREWRK zone.
- **AFX 3i DPL conflict:** `023` here vs `225` in the 6550, same frequency (456.800). One of the two is wrong.
- Adding Event One FX's digital contact as `Call1` would make a **fourth** `Call1` and a **second digital** `Call1` (the existing one is Call ID 1). Renaming the incoming one is now clearly necessary.
- Room is fine: one zone in use, three to add.

---

## Master codeplug — build plan

Target: one XPR 3500 codeplug carrying everything, zones kept separate by client.

| Zone | Source | Channels | Type |
|---|---|---|---|
| AMERICAN FIREWRK | 6550 codeplug | 10 | Analog, DPL 225 |
| 3CDC | 6550 codeplug | 2 | Analog, DPL 116 / 331 |
| Rozzi | 6550 codeplug | 16 | Analog, DPL 023 |
| Event One FX | CP200d codeplug | 4 | Digital, CC 4, TG 10010 |

32 channels, 4 zones. Both sources are different radio models from the XPR 3500, so neither can be Cloned in — the master gets built by hand in an XPR 3500 archive from the values in this file.

**Preserve everything (Brian, 2026-07-29).** All 20 contacts from the 6550 carry over as-is, including the 16 digital groups, both private calls, and the MDC and Quik-Call II entries, whether or not a channel references them. Rozzi 12 gets built as found (duplicate of Rozzi 11) unless Brian says otherwise. The empty RX group list and scan list come along too.

### Contacts in the master — 21 total

| Name | Type | Call ID | Source |
|---|---|---|---|
| GROUP 01 – GROUP 16 | Digital Group Call | 6100 … 7600 (hundreds) | 6550 |
| Portable | Digital Private Call | 1001 | 6550 |
| Base | Digital Private Call | 3001 | 6550 |
| Call1 | MDC Group Call | E001 | 6550 |
| Call1 | Quik-Call II | 138 | 6550 |
| *(digital group call)* | Digital Group Call | 10010 | Event One FX |

**Naming collision to settle:** the 6550 already carries two contacts named `Call1` (the MDC one and the Quik-Call II one), and the Event One FX digital contact is also named `Call1`. Three entries with one name makes the channel's Contact Name dropdown ambiguous. Recommend naming the incoming digital contact **`EVENT ONE FX`** instead — the alias is local to the codeplug and the Call ID 10010 is what actually has to match on the air, so nothing is lost. The four Event One FX channels then point at that name.

Build order: contacts → channels → zones → assign → scan/RX group lists.

---

## Decisions (Brian, 2026-07-29)

1. **AFX 3i = DPL 225** everywhere — the 023 in the 3500 was the typo.
2. **AFX 1i–4i get removed from Zone1** once the full AMERICAN FIREWRK zone exists. Zone1 drops to 11 channels.
3. ~~**The Event One FX digital contact keeps the name `Call1`**~~ — **dead, 2026-07-30. CPS makes it impossible.** Naming a second contact `Call1` red-flags the field and throws two validation errors (`\Contacts:Call1\Contact`, code `700101000`, "Invalid item needs to be removed") on *both* the new entry and the original, and a contact container accepts only **one** Digital entry, so nesting the 10010 call under the existing `Call1` isn't available either. The contact is named **`EVENT ONE FX`**. The alias is local to the codeplug; Call ID 10010 is what has to match on the air, so nothing is lost operationally.
4. **Zone1 → renamed `3CDC`.** Done 2026-07-30.
5. **Event One FX channels keep the source names `Channel1`–`Channel4`** — that's what their crew calls them over the air.
6. **Event One FX admit criteria = `Always`**, matching their source codeplug rather than the `Channel Free` used on Brian's own analog zones.

### Contacts actually needing to be added

The 3500 already carries `Call1`/MDC/E001 and `Call1`/Quik-Call II/138 — identical to two of the 6550's, so those are already preserved. To add: **GROUP 01–16** (digital group calls 6100–7600), **Portable** (private 1001), **Base** (private 3001), and the **Event One FX digital group call, ID 10010**. 19 new, 22 total.

### Zones actually needing to be built

| Zone | Channels | Note |
|---|---|---|
| AMERICAN FIREWRK | 10 analog, DPL 225 | AFX 3i corrected to 225 |
| Rozzi | 16 analog, DPL 023 | Rozzi 12 built as-found |
| Event One FX | 4 digital, CC 4, TG 10010 | contact = the `Call1` with ID 10010 |
| ~~3CDC (from the 6550)~~ | — | **redundant**, already in Zone1 as FSQ-PROD / WP-PROD |

30 new channels, not 32.

---

## Open items

*Settled 2026-07-30: AFX 3i DPL (225), AFX 1i–4i removed from Zone1, Zone1 renamed 3CDC, the Event One FX contact alias (`EVENT ONE FX`), and the Event One FX channel names (kept as `Channel1`–`Channel4`). What's left:*

1. **Rozzi 11 vs Rozzi 12** — identical frequency and DPL, built as found. Reads like a typo in the 6550; worth checking against Rozzi's own frequency list some day.
2. **Radio ID roster for the fleet** — every radio needs a unique one. Use **Clone**, not Clone Express, on new radios so the ID gets assigned during the push.
3. **Nothing has been written to a radio yet.** Verify one radio against one of Event One FX's on each channel before cloning out to the fleet.
4. **The other two fleet radios need the master pushed to them** — `867TTKA340` (6 analog venue channels, last programmed 2025-08-23) and `867TTF4358` (4 channels, last programmed **2017** — missing the Memo channels). Both are model `H02RDH9VA1AN`, same as the master's base radio, so Clone works.

---

## Build progress

**Working file:** `XPR3500 MASTER 2026-07-29.xctb` on the Surface machine's Desktop, saved from the loaded `867TTF2205` archive so the original is untouched. Format is *CPS Archive With Enhanced Protection (.xctb)* — the same as the other archives on that Desktop.

| Step | Status |
|---|---|
| Backup / master archive created | done |
| Zone `AMERICAN FIREWRK` created | done |
| 10 analog channels added and named (AFX 1i–5i, AFX 6–10 - Cinci) | done |
| Frequencies, DPL 225, admit criteria on those 10 | **done — 2026-07-30, verified** |
| Zone `Rozzi` + 16 channels | **done — 2026-07-30, verified** |
| Zone `Event One FX` + 4 digital channels | **done — 2026-07-30, verified** |
| 19 contacts | **done — 2026-07-30, verified** |
| Remove AFX 1i–4i from Zone1, rename Zone1 → 3CDC | **done — 2026-07-30, verified** |

**The master codeplug is complete.** Four zones, 41 channels, 22 contacts, validation 0, warnings 0, re-read from disk. Nothing has been written to a radio yet.

New channels default to: 403.025000 RX/TX, CSQ squelch, DPL code 023 greyed, power High, TOT 60, 12.5 kHz, **Admit Criteria `Channel Free`**, Unmute Rule `Std Unmute, Mute`, RSSI −124, TPL Reverse Burst Standard, and TX `DPL Turn-Off Code` auto-checks as soon as TX squelch is set to DPL. Every one of those already matches the 6550's common settings, so only four fields per channel actually need typing: RX frequency, RX DPL code, TX frequency, TX DPL code (plus the two squelch-type dropdowns). *(Corrects the earlier note that new channels default to admit `Always`.)*

### AMERICAN FIREWRK — as built and verified 2026-07-30

All 10 analog, simplex (TX = RX), 12.5 kHz, DPL **225** on both RX and TX, DPL Invert off both sides, admit `Channel Free`, power High, TOT 60 s / rekey 0, RSSI −124, no signalling system, no scan list.

| # | Name | RX = TX (MHz) |
|---|---|---|
| 1 | AFX 1i | 462.862500 |
| 2 | AFX 2i | 467.862500 |
| 3 | AFX 3i | 456.800000 |
| 4 | AFX 4i | 464.550000 |
| 5 | AFX 5i | 462.837500 |
| 6 | AFX 6 - Cinci | 464.825000 |
| 7 | AFX 7 - Cinci | 469.825000 |
| 8 | AFX 8 - Cinci | 464.125000 |
| 9 | AFX 9 - Cinci | 469.125000 |
| 10 | AFX 10 - Cinci | 467.850000 |

AFX 3i carries **225**, per decision 1 — the `023` in the 3500's Zone1 was the typo.

**Verification performed:** read every column of the zone-item grid back (RX freq/squelch/DPL/invert, TX freq/squelch/DPL/invert, unmute rule, VOX, reverse burst, power, TOT, rekey, admit, RSSI) → all 10 rows correct; Validation Results 0 items; Warning Messages 0 items; saved; then **closed and re-opened the archive from disk** and re-read the RX and TX columns to confirm the values persisted to the file, not just the in-memory model.

### Rozzi — as built and verified 2026-07-30

All 16 analog, simplex (TX = RX), 12.5 kHz, DPL **023** on both RX and TX, DPL Invert off both sides, admit `Channel Free`, power High, TOT 60 s / rekey 0, RSSI −124, unmute `Std Unmute, Mute`, TX DPL Turn-Off Code checked, no signalling system, no scan list.

| # | Name | RX = TX (MHz) |
|---|---|---|
| 1 | Rozzi 1 | 464.550000 |
| 2 | Rozzi 2 | 456.787000 |
| 3 | Rozzi 3 | 456.812000 |
| 4 | Rozzi 4 | 456.857000 |
| 5 | Rozzi 5 | 456.862000 |
| 6 | Rozzi 6 | 456.887000 |
| 7 | Rozzi 7 | 469.550000 |
| 8 | Rozzi 8 | 469.500000 |
| 9 | Rozzi 9 | 467.925000 |
| 10 | Rozzi 10 | 467.900000 |
| 11 | Rozzi 11 | 467.875000 |
| 12 | Rozzi 12 | 467.875000 |
| 13 | Rozzi 13 | 467.812000 |
| 14 | Rozzi 14 | 467.762000 |
| 15 | Rozzi 15 | 464.825000 |
| 16 | Rozzi 16 | 467.712000 |

**Rozzi 11 and 12 are both 467.875000 / DPL 023** — built as found, per the preserve-the-source decision. Still worth checking against Rozzi's own frequency list some day; it reads like a typo in the 6550.

**Build method — `Add Copies`, which is the fast path.** Configure channel 1 completely, select its row, ⋯ → `Add Copies` → 15. The copies carry **everything** — frequency, both squelch types, both DPL codes, admit, power, TOT, unmute, DPL turn-off — and arrive named `ChannelNN`. That leaves only **three fields per copy**: Channel Name, RX Frequency, TX Frequency. DPL 023 needed no typing anywhere in this zone because it's already the new-channel default.

**Zone capacity is 16 channels** — the ⊕ Add button greys out once a zone holds 16, which is exactly what Rozzi needs. Worth knowing before planning any zone bigger than that.

**Verification performed:** same pass as AMERICAN FIREWRK — all 16 rows read back across channel name, RX freq/squelch/DPL/invert, TX freq/squelch/DPL/invert, VOX, reverse burst, power, TOT, rekey, admit, RSSI; Validation Results 0 items; Warning Messages 0 items; saved; re-opened the archive from disk and re-read the names and RX/TX columns, and confirmed AMERICAN FIREWRK's 10 channels were still intact alongside it.

### Event One FX — as built and verified 2026-07-30

All 4 digital, simplex (TX = RX), **Color Code 4**, Repeater/Time Slot 1, Contact Name **EVENT ONE FX** (Call ID 10010), RX Group List None, Scan/Roam None, admit **Always**, In Call Criteria Always, power High, TOT 60 s / rekey 0, RSSI −124, privacy off, Extended Range Direct Mode Disabled, Data Call Confirmed on.

| # | Name | RX = TX (MHz) |
|---|---|---|
| 1 | Channel1 | 464.500000 |
| 2 | Channel2 | 464.550000 |
| 3 | Channel3 | 469.500000 |
| 4 | Channel4 | 469.550000 |

Built the same way as Rozzi: Channel1 configured in full, then `Add Copies` ×3. The copies carried color code, slot, contact, admit, power and TOT, so each cost only a name and its two frequencies. Copies arrive named `Channel43`/`44`/`45` — the numbering is global, not per-zone, so don't read anything into it.

**Verification performed:** read the zone grid back across name, color code, inbound/outbound color code, slot, scan list, RX frequency, RX group list, TX frequency, contact name, power, TOT, rekey, admit, in-call, RSSI — all 4 rows correct; Validation Results 0 items; Warning Messages 0 items; saved; closed and re-opened the archive from disk and re-read the names, RX and TX columns and the contact assignment.

### 3CDC (was Zone1) — trimmed and renamed 2026-07-30

AFX 4i, 3i, 2i, 1i deleted from positions 15→12 (bottom up, so the rows above never shift), leaving **11 channels**: FSQ-OPS, FSQ-PROD, FSQ-GARAGE, WP-OPS, WP-PROD, WP-GARAGE, OTR-DIST, MEM-PROD, MEM-FOH, ZIEGLER, BBB. The zone was then renamed `Zone1` → **`3CDC`**. The scan list `ScanItems/List1` is untouched and still attached to WP-OPS — none of the four deleted AFX channels were members, so nothing broke.

### Contacts — 22, verified from disk 2026-07-30

`Call1` MDC/E001 · `Call1` Quik-Call II/138 · `Call1` Digital Group Call/**1** (all three original to the 3500) · GROUP 01–16 digital group calls 6100–7600 · Portable digital private 1001 · Base digital private 3001 · **EVENT ONE FX** digital group call **10010**.

### Operating notes for driving CPS over AnyDesk

- **AnyDesk keyboard must be set to Keyboard → Local.** On Auto, every keystroke arrives garbled (typed text came through as a run of `aaaa…`). Fixed at the menu bar, not in the remote session.
- Grid cell editing pattern that works: **double-click the cell → click again inside the edit box → backspace to clear → type.** Double-click alone opens the editor but leaves focus elsewhere, so typing goes nowhere.
- Tree nodes usually need **two clicks** — the first selects, the second loads the pane.
- Adding a channel: select the zone → ⊕ → "Choose Set Type" dialog (defaults to Analog) → OK.
- `Shift`-click does **not** multi-select cells, so the manual's Fill Down gesture doesn't work over this link.
- **The ⋯ (3-dot) menu above the channel table has `Add Set`, `Add Multiple Sets`, `Add Copies`, `Move To Position`, `Copy`, `Paste`.** `Add Copies` duplicates a configured channel N times — the fast way to build the 16 Rozzi channels from one template. `Copy`/`Paste` is the documented CPS 2.0 → CPS 2.0 set-level transfer.
- **Edit the channel in its own form, not in the grid.** Select the row in the far-left selector column → the ✏ (pencil) button above the table → the channel opens as a form with `General` and `RX/TX` section tabs at the top. Clicking the `RX/TX` tab scrolls straight to the RX and TX field blocks, and the field positions are consistent from channel to channel, which makes the work batchable. Breadcrumb `Zone Items` goes back to the list.
- **`Ctrl+A` before typing in any field. Triple-click does NOT select the contents** — it leaves the caret in place, so the new text is *inserted* and you get a concatenated value. That's what threw `Value is out of Range` on the first frequency attempt (the field silently reverted and logged a warning). Click → `Ctrl+A` → type is reliable.
- Setting TX Squelch Type to DPL inserts the `DPL Turn-Off Code` row, which pushes every field in the RX/TX block down ~7 px. Do the two squelch dropdowns *before* typing the DPL codes, and re-read coordinates after.
- Two CPS windows: `middle-click` the taskbar icon to launch a second instance; hover the icon to get thumbnails and pick between them.
- **New zone:** click the gear on the `Zone` tree node → `Create New Set`. It lands as `ZoneN`; rename it in the Zone Name field. Then ⊕ → Choose Set Type (Analog) → OK adds a channel.
- **⊖ deletes a zone item with no confirmation prompt.** Select the row, click ⊖, it's gone. Delete bottom-up when removing a block of rows so the positions above never shift under you.
- **The form's General / RX/TX collapse state persists between channels.** Collapsing `General` to get at the RX/TX block shifts every field ~1 px and the next channel's form opens collapsed the same way — so re-read coordinates after the first channel of a batch rather than assuming the layout from the last one.
- **Reset the grid's horizontal scroll to the far left before clicking a row selector.** The selector column is the leftmost one, so if the grid is still scrolled right from a verification pass, the row never gets selected, the pencil does nothing, and the rest of a batched sequence lands on arbitrary cells — checkboxes included. Cost one wasted pass on 2026-07-30 (caught immediately on read-back, nothing altered). Drag the h-scrollbar thumb left, confirm the `Position` column is visible, then work; only scroll right again for verification at the end.

### Faster path worth taking

Building 30 channels field-by-field over AnyDesk is roughly 200 individual cell edits. Two ways to cut that down:

1. **Copy/paste between CPS instances.** The Event One FX archive is already on this machine's Desktop. If the 6550 archive (`376TVB1928.ctb2`, currently on the Broadcast machine) is copied over too, a second CPS window can open each source and the zones can be copied wholesale instead of retyped.
2. **`Add Copies`** — configure one channel fully, duplicate it 9 or 15 times, then change only the name and frequency per row. Cuts the per-channel work to two fields.

---

## Session log

**2026-07-30 (late)** — **Master codeplug finished.** Verified Channel1 of the Event One FX zone field by field, saved it as a checkpoint, then `Add Copies` ×3 and set the name and both frequencies on each — Channel2 464.550, Channel3 469.500, Channel4 469.550. Deleted AFX 4i→1i out of Zone1 bottom-up (positions 15 down to 12, so the rows above never shifted), leaving 11 channels, and renamed the zone `3CDC`. Saved, validation 0 / warnings 0, then closed the archive and re-opened it from disk and re-read all four zones, the Event One FX frequencies and contact assignments, and the full 22-contact table. Final state: **4 zones, 41 channels, 22 contacts, clean.** Two gotchas added to the operating notes — ⊖ deletes with no confirmation, and the form's section collapse state carries over to the next channel.

**2026-07-30** — Went looking for the 6550 archive on the Surface Desktop and it isn't there; the only archives on that Desktop are `867TTF4358.xctb`, `867TTKA340.xctb`, `Event One FX CP200 4 Channel Digital.xctb` and the master. Opened both unknown ones read-only: they're **two more XPR 3500s from the fleet**, same model `H02RDH9VA1AN` / Tanapa `PMUE3836BK` / codeplug 11.00.17 as the master's base radio — clone targets, not sources. `867TTKA340` (last programmed 2025-08-23, same day as 867TTF2205) holds 6 analog channels: FSQ-OPS, FSQ-PROD, WP-OPS, WP-PROD, MEM-PROD, MEM-FOH, no scan list. `867TTF4358` (last programmed 2017-07-31) holds only 4: FSQ-OPS, FSQ-PROD, WP-OPS, WP-PROD, with the scan list attached — nine years stale and missing the Memo channels. So the copy/paste shortcut is still blocked on `376TVB1928.ctb2`, which is on the Broadcast machine.

**Rozzi zone built the same session.** Created the zone, configured Rozzi 1 fully, then `Add Copies` ×15 — the copies carried every setting including DPL 023, so each one needed only a name and its two frequencies. Verified all 16 rows, validation and warnings clean, saved, re-opened from disk and re-read, and confirmed AMERICAN FIREWRK was untouched. One wasted pass along the way: the zone grid was still scrolled right from a verification check, so a batched row-select missed and the follow-on clicks landed on arbitrary cells — caught on read-back with nothing altered, and the fix is now in the operating notes.

Brian's call: build by hand. **Configured all 10 AMERICAN FIREWRK channels manually over AnyDesk** — frequencies, RX/TX squelch to DPL, DPL 225 both sides — then verified column by column, validation and warnings both clean, saved, and re-opened the archive from disk to confirm persistence. Table and verification detail under Build progress above; the CPS editing gotchas (Ctrl+A, the pencil form, the DPL row shift) are in the operating notes.

**2026-07-29** — Researched CPS (both products) and wrote the operator reference. Confirmed fleet is XPR 3500, UHF business band, no repeater. Drove AnyDesk to the remote PC and read the full Event One FX CP200d codeplug spec out of the loaded archive. Then read the XPR 6550 codeplug `376TVB1928.ctb2` on the second remote machine — all three zones, 28 channels, contacts, group list and scan list captured above. Read-only throughout; nothing written or modified in either codeplug.
