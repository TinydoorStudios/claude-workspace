# Motorola CPS — Operator Reference (Nyquist)

*Built 2026-07-29 from the MOTOTRBO CPS 2.0 Online Help (MN006055A01-AB, PCR 2.10.5), the Business Radio "Web CPS" help tree installed in Brian's Wine prefix, and Motorola/dealer programming guides. Purpose: let me drive CPS on a remote PC over AnyDesk without guessing.*

---

## 1. Know which CPS you're looking at

Three different products get called "CPS." They share concepts and share nothing else.

| Software | Radios | Archive format | UI |
|---|---|---|---|
| **MOTOTRBO CPS 2.0** | XPR / SL / DP / MOTOTRBO portables, mobiles, repeaters | `.ctb2` (also opens `.ctb` from CPS 1.0 if CPS 1.0 is installed, and `.xpba` from Radio Management) | Native Windows app: menu bar + Actions Bar + Set Categories tree |
| **Business Radio CPS** ("Web CPS") | CLS, CLP, Curve, DLR, DTR, RDX (RDU/RDV), RM | in-app **profiles**, plus `.wcp` model codeplugs on disk | Local web server (`127.0.0.1:9990`) rendered in a browser — HOME / RADIOS views |
| **RadioCentral** | R7 and newer | cloud/local library | separate client, not covered here |

Brian's Mac has both: MOTOTRBO CPS 2.0 installer `2.157.149.0` at `~/Desktop/CPS2_2.157.149.0/Installer.exe`, and Business Radio CPS installed into the Wine prefix at `~/.wine/drive_c/Program Files (x86)/Motorola Solutions/Business Radio CPS/`. There's an existing MOTOTRBO archive at `~/Desktop/AFX/AFX 6550.ctb2`.

**The remote PC's version is unconfirmed — verify from Help → About before touching anything.**

---

## 2. Codeplug ground rules

A codeplug is the radio's entire personality: channels, frequencies, PL/DPL, power, scan, buttons, IDs, passwords, tuning. Programming = editing a codeplug in CPS and writing it into the radio. You never type settings into the radio itself (except front-panel programming, if enabled).

`.ctb2` files are **encrypted** — header is `Copyright (c) 2023 Motorola Solutions, Inc. All Rights Reserved` followed by an encrypted blob. There is no external editor, no text diff, no scripted edit. Everything happens in the GUI. Same for the Business Radio `.wcp` and `config.xml` files, which are also encrypted on disk.

Consequence for AnyDesk work: every change is a GUI action, and the only safe rollback is a saved archive taken **before** the edit.

---

## 3. MOTOTRBO CPS 2.0

### Layout
Menu bar (File / Device / Licenses / Tools / Help) → Actions Bar of icons under it → **Set Categories** tree on the left (Device Information at top, then Set folders) → **Programming Pane** in the middle → **Information Windows** docked along the bottom (Validation Results, Warning Messages, Search Results, Help — hidden by default, click the tab to expand, pin with the horizontal Auto Hide pin).

*Sets and Configurations:* a **Set** is a logical group of fields (General Settings, Network, Contacts…). A **Configuration** is a collection of Sets tied to a product family. An archive = radio-specific data (model, version, options) + a configuration. Some Sets are single-instance (General Settings), others multi-instance (MDC Systems).

### Keyboard shortcuts
| Action | Key |
|---|---|
| Open archive | `CTRL+O` |
| Save | `CTRL+S` |
| Read radio | `CTRL+R` |
| Write radio | `CTRL+W` |
| Clone | `CTRL+F3` |
| Clone Express | `CTRL+F4` |
| Update firmware | `CTRL+U` |
| Context help on selected field | `F1` |

### Read a radio
Radio **powered off** when you attach the cable, then power it on, wait a few seconds for the PC to detect it, then `CTRL+R` / Device → Read. Multiple radios connected → a Connected Devices dialog appears; pick the target. A successful read replaces whatever archive is open in the pane (only one archive per CPS instance — open a second CPS window to compare two).

### Write a radio
Write requires the **serial number in the archive to match the radio**. Different serial, same model → use Clone or Clone Express instead.

1. Open the source archive (or read the radio).
2. Connect the target radio, power it on, wait.
3. `CTRL+W` / Device → Write.
4. **Do not disconnect the cable until the confirmation dialog appears.** Pulling it mid-write corrupts the radio.

On success the radio resets, and a locked/disabled radio becomes enabled. CPS programs the first channel in the zone as the default channel. Codeplug version mismatches are handled silently: a lower version in the radio gets the archive downgraded, a higher version gets it upgraded, and **any missing values are set to default** — so re-check anything unusual after a cross-version write.

If the archive has "available for purchase" features enabled that the radio doesn't have licensed, the write is refused until those features are registered and activated.

### Clone vs Clone Express
Same model, different serial, both required.

**Clone** (`CTRL+F3`) — pushes the source configuration and prompts you for the target's **Radio Identity Parameters** (Radio Alias, Radio ID, Radio IP, CAI Network, WAVE 5000 username/password, 5 Tone ID). This is the fleet-deployment path: clone → fill in the new identity → repeat per radio.

**Clone Express** (`CTRL+F4`) — pushes the source configuration and **preserves the identity already in the target radio**. This is the "push a settings change to an already-deployed fleet without stomping radio IDs" path.

### Update and Recover
**Update** (`CTRL+U`) writes new firmware, reading and upgrading the existing codeplug first, preserving the tuning block. **Recover** (Device → Recover) rewrites firmware plus a *default* codeplug — it revives a corrupted radio or returns it to out-of-box, preserving only the tuning block. Recover wipes all user-programmable fields; treat it as a last resort. Recover needs the FlashZap driver the first time.

### Licensing (features that cost money)
Two steps, both needing internet: **Register** (Licenses → Register Device Licenses, enter the EID, query, select features, add serial numbers by hand / CSV import / "Add all connected devices", Register) then **Activate** (Licenses → Activate Device Licenses on the *same PC* that registered, Read Features, select, Activate — radio resets). Digital and Digital Telephone Patch also need a firmware Update to finish activating. To see what a given radio can buy: read it, then click the top configuration node in Set Categories. Keep the EID — it's the only handle on purchased features.

### Editing efficiently in the Programming Pane
Row select by hovering the far-left column (pointer turns into a hand); `SHIFT`/`CTRL` for ranges. Buttons above list tables: Edit (pencil), Add, Delete, and a 3-dot for extras — a greyed button means the operation isn't supported there. Right-click a column header to open **Field Chooser** and hide columns; drag headers to reorder. **Fill Down**: select the source cell, hold `Shift`, select the target cells below, right-click → Fill down. The Search box filters rows within a table; the Search Results window (Name / Value / Name and Value, Match whole word) searches the whole configuration and double-clicking a hit jumps to the field.

**Validation Results** lists errors with Path / Error Code / Description; a curly "Reset Value" icon in the Actions column auto-fixes, and "Reset All (For Selected Top Set)" clears a whole set. Fix validation errors *before* writing.

Copy/paste works at Set level between two CPS 2.0 instances (and into Radio Management's Configuration Client). Named references resolve by name — paste a personality that points at contact "Call 1" into a configuration lacking "Call 1" and the field goes NULL and invalid. Pasting a same-named set overwrites it. Anything that fails to copy shows in Warning Messages.

### Where things live (Set map, abridged)
Device Information (read-only: Model, Tanapa, Region, Serial, Firmware ID/Type/Version, Codeplug Version, Frequency Range, Last Programmed Date) · General Settings (power-up, alerts, battery, mic/audio profile, backlight, Password and Lock, Front Programming Password, Delete All, Rental Timer) · Accessories (GPIO pins, wireline, Bluetooth) · Control Buttons (per-model portable/mobile button and accessory-button assignment, One Touch Access) · Text Messages · Menu · Security · Network (**Radio IP lives here**) · Talkgroups · Voice Announcement · Signaling Systems / MDC / Quik-Call II / 5 Tone · **Contacts** (Digital: Call Type, Contact Name, Call ID, Route/Connection Type, ring style) · **Digital RX Group List** · **Personality** (the channel: Channel Type, Channel Name, Bandwidth, Scan/Roam List, Auto Scan, Color Code, Squelch, Allow Talkaround, Mandown, Lone Worker, plus RX/TX frequency, TG, admit criteria) · **Zone** · **Scan / Scan Items** · Roam · Capacity Plus lists.

Reports: File → Reports… gives Channel Summary and Customer Handout (dealer block comes from Tools → Settings → Dealer Info).

### Troubleshooting (from the manual)
Can't read or write: cable seated at both ends, radio powered on, portable battery not low, MOTOTRBO network-connection icon present in the taskbar, MOTOTRBO driver installed under Network Adapters, model supported, radio's codeplug major version not newer than CPS. Multiple radios connected → the **third octet of each Radio IP must differ** (192.168.10.1 / 192.168.11.1 good; 192.168.10.1 / 192.168.10.2 bad). Archive-side: Check for Password set to Read Only, Read/Write and Codeplug Password blank. Mobiles: the front connector wins over the rear; after removing a front cable the radio needs a hard reset before the rear one works.

The radio appears to Windows as a network interface, and other bindings on that adapter can break CPS operations — fix by opening that adapter's properties and unchecking everything except Internet Protocol (TCP/IPv4). Has to be redone every time the driver is reinstalled.

Logs: `%programdata%\Motorola\MOTOTRBO CPS 2.0\Log`.

---

## 3a. Brian's fleet: XPR 3500, business band — analog vs digital channels

Confirmed 2026-07-29: XPR 3500 portables, UHF business band, MOTOTRBO CPS 2.0. This is the MOTOTRBO path, not Business Radio CPS.

### Where the switch lives
Channel type is a **per-channel property of the Personality set**, not a radio-wide mode. In the Set Categories tree, open the channel under the Channels folder → **General** section → **Channel Type** dropdown → `Analog` or `Digital`. (The dropdown also lists Capacity Plus variants, Dynamic Mixed Mode, 5 Tone, Capacity Max Trunking and WAVE — none apply to a conventional business-band fleet.) Changing it swaps the entire field set below it. Requires the Conventional Capable feature enabled.

**Prerequisite:** Device Information → **Firmware Type** must read `Digital` (the manual defines Analog = analog-only firmware, Digital = analog *and* digital). If a radio reads back Analog, digital channels aren't available until the Digital feature is registered/activated and a firmware Update is written.

A zone can hold analog and digital channels side by side — that's the normal migration layout, and how you keep a legacy analog channel on the same knob position range as the digital ones.

### Analog channel — the fields that matter
| Field | Notes |
|---|---|
| Channel Bandwidth | 12.5 kHz. CPS blocks 20/25 kHz for Part 90 VHF/UHF in the US per the FCC narrowbanding mandate |
| RX/TX Frequency | Same for simplex/talkaround; different for a repeater pair |
| RX Squelch Type | `CSQ` / `TPL` / `DPL` |
| RX TPL Frequency or Code | 67.0–255.0 Hz, 0.1 Hz steps; setting the code auto-fills the frequency |
| RX DPL Code (Octal) + DPL Invert | 000–777 octal |
| TX Squelch Type + TX TPL/DPL | Set independently of RX |
| Unmute Rule | `Std Unmute, Mute` / `And Unmute, Mute` / `And Unmute, Or Mute` — only when RX squelch isn't CSQ |
| Squelch / Squelch Level | Normal / Tight; Specific unlocks the 0–14 level (repeater only) |
| Admit Criteria | `Always` (impolite), `Channel Free` (polite to all), `Correct PL` (needs TPL/DPL on RX) |
| TPL Reverse Burst, Voice Emphasis, VOX, Power Level, TOT | Standard analog housekeeping |
| RX/TX Signaling System | MDC / Quik-Call II if used — otherwise None |

### Digital channel — the fields that matter
| Field | Notes |
|---|---|
| Channel Bandwidth | Fixed 12.5 kHz, not editable |
| RX/TX Frequency | **Equal = direct/talkaround. Different = repeater channel** — MOTOTRBO has no direct-mode channel with split frequencies |
| Color Code | 0–15, identifies the system; radios ignore activity with a mismatched color code. Must match the repeater |
| Repeater/Time Slot | Slot 1 or 2 (repeater mode only). Radios that must talk together share frequency **and** slot |
| Contact Name | The talkgroup/call the PTT initiates. Build it in the Contacts folder first |
| Group List | The RX Group List — what the radio hears. The Contact's Call ID is auto-included even if this is None |
| Admit Criteria | `Always`, `Channel Free`, `Color Code Free` (polite to own digital system) |
| Privacy | Basic Privacy checkbox; every radio needs the same key. Not encryption — anti-eavesdropping only |
| Emergency System | Digital emergency system, or None |
| IF Filter Type | Digital channels only; Narrow at 12.5 kHz adjacent spacing buys 3–4 dB ACS at 0.5 dB sensitivity |
| Allow Talkaround | Needs RX and TX frequencies to differ; disabled if RX Only is set |

Analog-only concepts that vanish on a digital channel: squelch type/PL codes, unmute rule, squelch level, signaling systems. Digital-only concepts that vanish on analog: color code, time slot, contact/group list, privacy, IF filter.

### Digital direct mode (no repeater) — Brian's case, confirmed 2026-07-29

No repeater in the system, so every digital channel is direct/simplex:

| Field | Value |
|---|---|
| RX Frequency / TX Frequency | **identical** — that's what makes it a direct-mode channel |
| Repeater/Time Slot | not applicable in direct mode (only Repeater mode and DCDM use it) |
| Color Code | pick one, e.g. `1`, and use the same on every radio and channel — mismatches are silently ignored traffic |
| Contact Name | one Group Call contact, same talkgroup ID fleet-wide |
| Group List | can stay `None` for a single-talkgroup setup — the Contact's Call ID is auto-received. Build a list only to hear extra talkgroups |
| Admit Criteria | `Channel Free` on shared business-band frequencies — it's polite to analog users too. `Color Code Free` only respects our own digital traffic and will transmit over an analog conversation |
| Allow Talkaround | greys out, and correctly so — the channel is already direct |
| Privacy | optional; the same Basic Privacy key on every radio, or nobody decodes |
| Radio ID | unique per radio (Network set / Radio Identity Parameters) — needed for private calls, not for group calls |

Direct mode carries **one conversation per frequency** — no second time slot without a repeater. Dual Capacity Direct Mode does give two simultaneous transmissions in the same 12.5 kHz by having the radios elect a timing leader and track slot structure, but every radio must be enabled for it, one radio must be provisioned Preferred timing leader (something always on, wide coverage, never scanning), and it disables talkaround and caps color code at 0–14. Not worth it for a small direct fleet.

**Don't put an analog channel and a digital channel on the same frequency.** A digital transmission is noise to an analog radio and vice versa, and neither side's squelch protects the other.

### Captured source codeplug — "Event One FX CP200 4 Channel Digital" (read 2026-07-29 over AnyDesk)

Source radio is a **CP200d**, not an XPR — Model `H01QDC9JA2AN`, Tanapa `PMUE4147BA`, region NA, serial `752TVH1767`, UHF 403–470 MHz, Firmware Type `Digital`, firmware `R01.01.30.0000`, codeplug version `11.00.46`, last programmed 2026-02-03.

Zone1, four digital channels, all direct (TX = RX):

| # | Name | Type | RX = TX (MHz) | Color Code | Slot | Contact | RX Group List | Admit | Power | TOT | Privacy |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Channel1 | Digital | 464.500000 | 4 | 1 | Call1 | None | Always | High | 60 s | No |
| 2 | Channel2 | Digital | 464.550000 | 4 | 1 | Call1 | None | Always | High | 60 s | No |
| 3 | Channel3 | Digital | 469.500000 | 4 | 1 | Call1 | None | Always | High | 60 s | No |
| 4 | Channel4 | Digital | 469.550000 | 4 | 1 | Call1 | None | Always | High | 60 s | No |

Contacts: a single entry **`Call1` — Digital Calls, Group Call, Call ID `10010`**. The Digital RX Group List `List1` exists but is **empty** (Call1 sits in Available, Members blank) and no channel references it — reception rides on the contact's auto-included Call ID.

Also on every channel: Scan/Roam List `None`, Auto Scan No, ARS Disabled, RAS `None`, Allow Talkaround greyed (correct — TX=RX), Extended Range Direct Mode Disabled, DCDM unchecked, Timing Leader Eligible, RX Only unchecked, TX VOX off, TOT Rekey Delay 0, In Call Criteria Always, RSSI threshold −124 dBm, Private Call Confirmed off, Data Call Confirmed on, Enhanced Channel Access No. Network set is stock: Radio IP 192.168.10.1, CAI Network 12, CAI Group Network 225.

The scan list `List1` under Scan Items has members "Selected" + Channel1, but since no channel points at it, scan is effectively off.

Frequencies are the classic UHF itinerant business pairs — 464.500/469.500 (red dot) and 464.550/469.550 (blue dot) — run here as four simplex channels rather than two repeater pairs.

**Cross-model caveat:** a CP200d codeplug can't be Cloned or Clone-Expressed onto an XPR 3500 — both operations require the same model. Set-level copy/paste between two CPS 2.0 instances is possible, but with four channels, retyping them into the XPR archive is faster and less likely to drag CP200d-specific baggage across. The values above are the whole spec.

### Order of operations for a mixed fleet
Contacts (talkgroups) → RX Group Lists → Channels (set Channel Type first, then fill the type-specific fields) → Zones (assign and order the channels) → Scan lists last, since a scan list references finished channels. Scan hang time is set separately for digital and analog under the Scan set.

Deploy: build and verify one radio, save the archive, then **Clone Express** to the rest so each radio keeps its own Radio ID and alias.

---

## 4. Business Radio CPS (CLS / CLP / Curve / DLR / DTR / RDX / RM)

### What it is
A local service (`RMCPS.exe`, `RMCPSAgent.exe`, two Windows services) serving a web UI on `http://127.0.0.1:9990`; `WebLauncher.exe` just opens that URL in the default browser. Officially Windows 10 21H2+/11, IE 8+/Safari 5+/Firefox 5+/Chrome 13+. The USB driver installs with the software.

Internal model families in the install (help tree + GUI XML): `CLP`, `DLRX`, `DTR`, `FIJI`, `NOME`, `MURNOME`, `SOLO`, `MURSOLO`, `RENOIR`, `VANU`. On-disk `.wcp` codeplug templates cover CLP (CLU…), Curve (CU/NCU…), DLR1020/1060/110N, DTR (DTS130N/DTS150N), RM (RMM2050, RMU2040/2043/2080, RMV2080), RDX (RU4100/4160, RV5100) and D410/D550/D650.

### Views and documents
**HOME** holds My Profile — Language, **Dealer Login** (dealer PIN), Help Pane toggle — and Dealer Info for the Customer Handout. **RADIOS** is where profiles live.

| Action | Where |
|---|---|
| New profile | left pane → **New** → pick Radio Type, then model or a saved profile |
| Open saved profile | left pane → **Open** |
| Read radio | left pane → **Read from the radio** |
| Save inside CPS | top of profile view → **Save to profile** |
| Save to a file | **Save As** |
| Write radio | **Write** / **Write to radio** |
| Restart radio from PC | **Reset** (only on profiles under the Radio section) |
| Reports | **Customer Handout** (serial, model, hardware) · **Detailed Report** (full config dump) |

### Read / write specifics
Radio **powered up**, cable in USB, and — this is the one people miss — the **switch on the cable must be in the right position**: `CPS` for read/write; on the older desktop CPS the guidance is *Analog* for everything except DLR/DTR, which need *Digital*. RDX radios need the short pigtail.

Read prompts for the 4-digit codeplug password if one is set, and refuses if the radio's region isn't supported by the CPS or its codeplug version is newer than the CPS supports. Write prompts for the password too. Never unplug during a write.

**Cloning across models** is allowed only when: same band (UHF→UHF, VHF→VHF), same region, equal codeplug version, equal serial-clone compatibility. Channel counts may differ — extra channels beyond the target's max are dropped with a warning.

### Editing the codeplug
**Channels** table — Name, Mode, Frequency, Bandwidth, PL/DPL Code are editable inline; **Edit More** opens the full per-channel view. Add appends a channel (greyed at the model's max); Delete removes selected (minimum one channel must remain).

Channel Name: max 8 characters, unique, can't be blank. Per-channel fields worth knowing: **Repeater** checkbox (checked = repeater mode, unchecked = talkaround; if RX and TX params match, the channel is permanently talkaround and the box greys out), **Scramble** (Off / codes 1–3 — privacy, not encryption), **Auto Scan** (non-display models), **Dynamic Talkaround Scan**, **Disable Channel** (removes it from the scan list and bonks on non-display radios).

**RF Frequency** table — the frequency pool the channels draw from: Frequency (MHz), Bandwidth, Power Level, Compander. **Editing or adding frequencies is dealer-gated** — the help states the *dealer* adds/edits frequencies, and the Dealer PIN goes in HOME → My Profile → Dealer Login. Without it you can only pick from the factory-populated table. Deleting a frequency only works if no channel references it, and references after it shift up.

Bandwidth choices are `12.5 kHz only`, `25 kHz only`, or user-selectable with either as default; picking "user selectable" is what makes the per-channel RX/TX Bandwidth field editable. Power Level works the same way (Low ≈ 1 W, or 2 W on a 4/5 W radio; High ≈ 2 W, or 4/5 W). Compander is only offered at 12.5 kHz.

**PL/DPL codes** are index numbers 0–219: `0` = none, `1–122` standard, `123` = DPL 645, `124–129` customized PL, `130–213` inverted DPL, `214–219` customized DPL. Available count is model-dependent. Customized PL takes a frequency 67.0–255.0 Hz; customized DPL takes an octal code 001–777. The full CTCSS/DPL table is in the local help at `bin/htdocs/help/<FAMILY>/Fen_us/channels/ctcss_dpl_code_table.htm`.

**Matching an existing fleet: both the carrier frequency AND the PL/DPL code must match.** New fleet — pick any code from the list.

**Scan List** — two panes, Available Channels and Scan List Members, moved with Add / Remove. A channel in the members list leaves the available list.

**General Settings** — Codeplug Password (4-digit PIN, plus Confirm; once set the radio can only be read with it, and it shows as `****` on subsequent reads), Transmit Timeout Timer (60/120/180 s), PL Reverse Burst (180/240), Battery Save (off costs ~20% runtime), Disable All LEDs, Enable Programming Mode (front-panel programming), Enable Restore Factory Default, Power Up Text (8 chars, display models), Backlight.

**DLR / DTR digital side** — Public Groups (top 20 are fixed and undeletable), Private Groups, Privates, Favorite Contacts, and **Profile ID** (0000–9999; defines the IDs and frequency hopset of the first 20 public groups — `0000` is the DTR-compatible default). Changing Profile ID re-keys which radios can hear each other, so it matches across a fleet or nothing talks. DLR also carries Wi-Fi/cloud settings (SSID, security type, password, dealer token, telemetry).

### Troubleshooting
Can't read: cable connected to radio and USB, radio on, radio **not in Clone mode**. `CHAN 04` on screen is an alias, not a channel number. On this Mac's Wine install, the app's own web UI refuses to render in Chromium ("This page isn't supported by your browser") — the Mac copy is useful as a documentation source, not as a working programmer.

---

## 5. Operating over AnyDesk

- Set AnyDesk's **Keyboard → Local** (menu on the AnyDesk window) or typed characters arrive garbled on the remote box. This has bitten us before.
- Screenshot-verify state before every destructive action: which archive is open, which radio is selected in Connected Devices, which serial number.
- **Save a backup archive before any edit** (`Save As` with a dated name). It's the only rollback.
- Never let the session drop mid-write. If AnyDesk is unstable, stage edits, save the archive, and write when the link is solid.
- Cable switch position and radio power state are physical — I can't verify them from here. Those steps are Brian's, and I should ask rather than assume.
- Radio serial numbers, EIDs, and codeplug PINs are sensitive; keep them out of anything that leaves the machine.

---

## 6. Local sources I can re-read

| What | Path |
|---|---|
| MOTOTRBO CPS 2.0 Online Help, full text (36k lines) | scratchpad `cps20_guide.txt`, source PDF cached in this session's tool-results |
| Business Radio CPS help tree (10 model families, ~3,500 topics) | `~/.wine/drive_c/Program Files (x86)/Motorola Solutions/Business Radio CPS/bin/htdocs/help/` |
| Per-model GUI field definitions (encrypted) | same install, `data/gui/*GUI.xml` |
| `.wcp` model codeplug templates | same install, `data/cp/` |
| Existing MOTOTRBO archive | `~/Desktop/AFX/AFX 6550.ctb2` |
| CPS 2.0 installer 2.157.149.0 | `~/Desktop/CPS2_2.157.149.0/Installer.exe` |

---

## 7. Open questions for Brian

1. Which radios are we programming — MOTOTRBO (XPR/SL) or business-band (CLP/DLR/DTR/RM/RDX)? That decides which software and which whole workflow applies.
2. Which CPS is on the remote PC, and what version (Help → About)?
3. Is there a dealer PIN available? Without it, frequency-table edits are locked on the Business Radio side.
4. What's the actual job — new fleet from scratch, add radios to an existing fleet, or change settings on radios already deployed? Those are three different operations (Write vs Clone vs Clone Express).

*Sources: MOTOTRBO CPS 2.0 Online Help MN006055A01-AB (Motorola Solutions, July 2019); Business Radio CPS local help tree (Web CPS 1.0.0.0); Motorola Solutions Business Radio CPS product page; acmetool "How to Guide – Programming Motorola Business Radios" (CPS 7.0).*
